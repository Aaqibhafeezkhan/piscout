"""給新手用的健康檢查與一鍵快速設定。

健康檢查：在樹莓派上收集一組讀取用的數值，換成白話的結論與建議。
快速設定：只提供下面寫死的幾個動作，前端只能指定動作代號，不能送任意指令。
"""
from . import remote
from .i18n import tr

# 只讀取，不改任何東西
HEALTH_SH = r"""
t=$(vcgencmd get_throttled 2>/dev/null | cut -d= -f2); echo "throttled=$t"
temp=$(vcgencmd measure_temp 2>/dev/null | sed 's/[^0-9.]//g')
if [ -z "$temp" ] && [ -r /sys/class/thermal/thermal_zone0/temp ]; then
  temp=$(awk '{printf "%.1f", $1/1000}' /sys/class/thermal/thermal_zone0/temp)
fi
echo "temp=$temp"
echo "disk=$(df -P / | awk 'NR==2{gsub("%","",$5); print $5}')"
echo "memtotal=$(awk '/MemTotal/{print $2}' /proc/meminfo)"
echo "memavail=$(awk '/MemAvailable/{print $2}' /proc/meminfo)"
if dmesg >/dev/null 2>&1; then
  echo "sderr=$(dmesg 2>/dev/null | grep -ciE 'mmc[0-9]*:.*(error|timeout)|blk_update_request: I/O error|EXT4-fs error')"
else
  echo "sderr=-1"
fi
if command -v systemctl >/dev/null 2>&1; then
  echo "failed=$(systemctl --failed --no-legend --plain 2>/dev/null | awk '{print $1}' | tr '\n' ',')"
fi
echo "ntp=$(timedatectl show -p NTPSynchronized --value 2>/dev/null)"
"""


def parse(out):
    raw = {}
    for line in out.splitlines():
        k, sep, v = line.partition("=")
        if sep:
            raw[k.strip()] = v.strip()
    return raw


def _num(raw, key, cast=float):
    try:
        return cast(raw.get(key, ""))
    except ValueError:
        return None


def evaluate(raw):
    """回傳 [{id, level: ok|warn|bad, title, detail}]，文字已依目前語言翻好。"""
    out = []

    def add(id_, level, title, detail=""):
        out.append({"id": id_, "level": level, "title": title, "detail": detail})

    th = raw.get("throttled", "")
    bits = None
    if th.lower().startswith("0x"):
        try:
            bits = int(th, 16)
        except ValueError:
            pass
    if bits is not None:
        if bits & 0x1:
            add("power", "bad", tr("電源電壓不足（現在）"),
                tr("樹莓派正在被電源拖累，可能卡頓、當機或損壞 SD 卡。請換官方電源供應器，並避免太細太長的線。"))
        elif bits & 0x10000:
            add("power", "warn", tr("開機以來曾經電壓不足"),
                tr("電源曾經不穩。若發生過當機或卡頓，請換官方電源供應器與品質好的線。"))
        else:
            add("power", "ok", tr("電源正常"))
        if bits & 0xC:
            add("throttle", "bad", tr("正在降速保護"),
                tr("溫度太高或電壓不足，CPU 被強制降速。請加散熱片或風扇，並改善通風。"))
        elif bits & 0xC0000:
            add("throttle", "warn", tr("開機以來曾經降速"), tr("曾經過熱或電壓不足，建議加強散熱。"))

    temp = _num(raw, "temp")
    if temp is not None:
        if temp >= 80:
            add("temp", "bad", tr("CPU 溫度 {t} °C，太高了", t=temp), tr("請加散熱片或風扇，並改善通風。"))
        elif temp >= 70:
            add("temp", "warn", tr("CPU 溫度 {t} °C，偏高", t=temp), tr("長時間高負載建議加散熱片。"))
        else:
            add("temp", "ok", tr("CPU 溫度 {t} °C", t=temp))

    disk = _num(raw, "disk", int)
    if disk is not None and 0 <= disk <= 100:
        if disk >= 95:
            add("disk", "bad", tr("儲存空間快滿了（已用 {p}%）", p=disk),
                tr("空間滿了系統會出問題。請刪掉不用的檔案，或換更大的 SD 卡。"))
        elif disk >= 85:
            add("disk", "warn", tr("儲存空間偏少（已用 {p}%）", p=disk), tr("建議清理檔案。"))
        else:
            add("disk", "ok", tr("儲存空間足夠（已用 {p}%）", p=disk))

    total, avail = _num(raw, "memtotal", int), _num(raw, "memavail", int)
    if total and avail is not None:
        pct = avail * 100 // total
        if pct < 5:
            add("mem", "bad", tr("記憶體幾乎用完（剩 {p}%）", p=pct), tr("請關掉不需要的程式，或考慮加大 swap。"))
        elif pct < 10:
            add("mem", "warn", tr("記憶體偏少（剩 {p}%）", p=pct), tr("請留意正在執行的程式。"))
        else:
            add("mem", "ok", tr("記憶體充足（剩 {p}%）", p=pct))

    sd = _num(raw, "sderr", int)
    if sd is not None and sd >= 0:
        if sd > 0:
            add("sd", "bad", tr("系統記錄到 {n} 筆 SD 卡讀寫錯誤", n=sd),
                tr("SD 卡或電源可能有問題。請先備份重要資料，再換一張卡或改善供電。"))
        else:
            add("sd", "ok", tr("沒有 SD 卡讀寫錯誤"))

    failed = [u for u in raw.get("failed", "").split(",") if u]
    if failed:
        add("services", "warn", tr("有 {n} 個服務啟動失敗：{names}", n=len(failed), names=", ".join(failed[:5])),
            tr("可以在終端機用 systemctl status 服務名稱 查看原因。"))
    elif "failed" in raw:
        add("services", "ok", tr("所有服務都正常"))

    if raw.get("ntp") == "no":
        add("ntp", "warn", tr("時間沒有同步"),
            tr("時間不準會讓 apt 更新和 HTTPS 出現憑證錯誤。可以到「系統資訊」分頁的「快速設定」開啟時間同步。"))
    return out


def health(client):
    code, out, err = remote._run_script(client, HEALTH_SH, timeout=30)
    return evaluate(parse(out))


# ---------------------------------------------------------------- 快速設定
# status 印出 0 代表已經是開啟/完成的狀態；apply 用 sudo 執行
ACTIONS = {
    "i2c": {
        "title": "開啟 I2C", "desc": "接感測器、OLED 螢幕常用的介面。",
        "status": "raspi-config nonint get_i2c", "apply": "raspi-config nonint do_i2c 0", "reboot": True},
    "spi": {
        "title": "開啟 SPI", "desc": "接 LED 燈條、顯示器等硬體常用的介面。",
        "status": "raspi-config nonint get_spi", "apply": "raspi-config nonint do_spi 0", "reboot": True},
    "ntp": {
        "title": "開啟時間同步", "desc": "自動校準時間，避免更新和憑證出錯。",
        "status": '[ "$(timedatectl show -p NTPSynchronized --value 2>/dev/null)" = yes ] && echo 0 || echo 1',
        "apply": "timedatectl set-ntp true", "reboot": False},
    "tools": {
        "title": "安裝常用工具", "desc": "htop（看資源）、git、tree、ncdu（看哪些檔案佔空間）、curl。",
        "status": "dpkg -s htop git tree ncdu curl >/dev/null 2>&1 && echo 0 || echo 1",
        "apply": "apt-get install -y htop git tree ncdu curl", "reboot": False, "timeout": 300},
    "expand": {
        "title": "把檔案系統擴展到整張卡", "desc": "新燒錄的系統通常已自動擴展；若空間比卡小很多才需要。重開機後生效。",
        "status": ('r=$(lsblk -bnro SIZE /dev/mmcblk0p2 2>/dev/null); d=$(lsblk -bndo SIZE /dev/mmcblk0 2>/dev/null); '
                   'if [ -z "$r" ] || [ -z "$d" ] || [ $((r*100/d)) -ge 90 ]; then echo 0; else echo 1; fi'),
        "apply": "raspi-config nonint do_expand_rootfs", "reboot": True},
}


def _is_done(client, spec):
    code, out, _ = remote.run(client, spec["status"], timeout=20)
    return out.strip().splitlines()[:1] == ["0"]


def setup_status(client):
    """所有項目的狀態一次查完（一次往返，比一項一項查快很多）。"""
    script = chr(10).join('echo "%s=$( { %s; } 2>/dev/null | head -1 )"' % (k, v["status"]) for k, v in ACTIONS.items())
    code, out, _ = remote._run_script(client, script, timeout=30)
    raw = parse(out)
    return [{"id": k, "title": tr(v["title"]), "desc": tr(v["desc"]), "done": raw.get(k) == "0"}
            for k, v in ACTIONS.items()]


def setup_apply(client, action, sudo_password):
    spec = ACTIONS.get(action)
    if spec is None:
        raise remote.RemoteError(tr("不支援的操作"))
    code, out, err = remote.run(client, spec["apply"], sudo_password=sudo_password,
                                timeout=spec.get("timeout", 60))
    if code != 0:
        raise remote.RemoteError(tr("{cmd} 指令失敗：{err}", cmd=tr(spec["title"]),
                                    err=(err or out).strip()[-300:]))
    return {"id": action, "done": _is_done(client, spec), "reboot": spec["reboot"]}

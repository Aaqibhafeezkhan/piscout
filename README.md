# piscout

> Raspberry Pi 區網管理工具：自動掃描、內建 SSH 終端機、遠端桌面、遠端重灌系統。
> A Windows desktop tool to discover, SSH into, view the desktop of, and re-image Raspberry Pis on your LAN.

`raspberry-pi` `raspberry-pi-os` `network-scanner` `lan-discovery` `fleet-management`
`ssh-terminal` `remote-desktop` `vnc` `sd-card` `flasher` `imager` `netboot` `pxe`
`mdns` `fastapi` `pywebview` `windows` `desktop-app`

家裡有好幾台樹莓派，每次都要去路由器後台翻 IP、開 SSH 視窗、插拔 SD 卡重灌，
很煩。所以寫了這個 Windows 桌面程式，把這些事放在同一個視窗裡：

- **自動掃描**：一打開就掃區網，找出樹莓派
- **內建終端機**：點「連線」輸入帳密，直接在程式裡開 SSH 終端機，不用另外開視窗
- **遠端桌面**：一鍵看到樹莓派的桌面畫面並操作（走 SSH 通道）
- **遠端重灌**：SD 卡不用拔，從電腦直接把新系統寫進 Pi 的卡，並依型號給出最佳建議
- **本機燒錄**：也可以把 SD 卡插在電腦上燒錄
- **總覽與批次操作**：多台 Pi 的溫度、負載、記憶體一覽，勾選後可批次重開機、關機、更新套件
- **記住帳密**：以 Windows DPAPI 加密儲存，下次自動填入、自動偵測型號
- **雙語介面**：自動偵測系統語言（中文 / English），也可手動切換
- 系統映像全部來自樹莓派官方網站，會校驗 SHA-256

English: see [README.en.md](README.en.md).

目前還是早期版本，終端機與掃描有實測，遠端桌面和遠端重灌還需要更多實機驗證（見最下面）。

## 使用

到 [Releases](../../releases) 下載 `piscout.exe` 雙擊即可（尚未發佈時請依下方「從原始碼執行」自行打包）。
要寫入磁碟所以會跳出系統管理員確認，這是正常的。

> 檔案沒有簽章，SmartScreen 可能警告，按「其他資訊 → 仍要執行」。

### 連線、終端機、遠端桌面

開啟後會自動掃描。找到的樹莓派按「連線」，輸入帳號密碼，就會在程式裡開出終端機。
上方可以切換：

- **終端機**：完整的 xterm，支援縮放視窗
- **遠端桌面**：在 Pi 上啟動只監聽 `127.0.0.1` 的 wayvnc，再經 SSH 通道轉到程式裡顯示。
  需要 Raspberry Pi OS 桌面版（Wayland），Lite 版沒有桌面所以不行
- **系統資訊**：型號、溫度、記憶體、磁碟，並可安裝監控用的 agent

帳密只存在這個視窗的記憶體裡，關閉連線就沒了。

### 遠端重灌（SD 卡留在 Pi 上）

1. 到「燒錄系統」，選區網裡的樹莓派，填它**目前**的登入帳密
2. 按「讀取這台的型號與系統」，會自動選對型號並顯示最佳建議
3. 設定重灌後的主機名稱、帳號、密碼、Wi-Fi
4. 按兩次「開始燒錄」（第一次只是確認），等 10–30 分鐘，Pi 會自己重新開機

**前提：Pi 必須還開得起來、而且開著 SSH。** 完全空白的 SD 卡在網路上根本看不到，
沒有任何軟體能遠端連上它。這種情況請改用「插在這台電腦上的 SD 卡」。

運作方式：

1. 電腦端下載官方映像，解壓縮時把開機設定直接寫進映像裡的 boot 分割區
2. 把 `dd`、`dash`、`sha256sum` 連同函式庫複製到 Pi 的記憶體（`/dev/shm`），
   之後只用記憶體裡的程式，不再依賴會被覆蓋的 SD 卡
3. 映像串流經 SSH 寫入 Pi 的開機磁碟
4. 讀回前段資料算 SHA-256，**一致才重新開機**；不一致就停下來並報錯

> 這是在「正在執行的系統」上覆寫它自己的磁碟，天生有風險。寫到一半斷電或斷網，
> 那張卡就開不了機，得拔下來用電腦重燒。請在穩定的電源與網路下進行。

### 本機燒錄

「燒錄系統」選「插在這台電腦上的 SD 卡」。只列出 USB/SD 類的可移除磁碟，
不會列出系統碟，也不會列出超過 512 GB 的磁碟。

## 和其他工具的差別

| 工具 | 掃描 | 內建終端機 | 遠端桌面 | 燒錄 | 遠端重灌（不拔卡） |
|---|---|---|---|---|---|
| [Raspberry Pi Imager](https://github.com/raspberrypi/rpi-imager)（官方） | | | | 本機 SD 卡 | |
| Angry IP Scanner、各種 nmap 腳本 | ✓ 只列 IP | | | | |
| [LabLink](https://github.com/X9X0/LabLink) 等 Pi 掃描工具 | ✓ | | | | |
| Raspberry Pi Connect（官方） | | | ✓ 需帳號、走雲端 | | |
| **piscout** | ✓ | ✓ | ✓ | ✓ | ✓ |

piscout 不是要取代 Imager：Imager 是把映像寫進一張卡，piscout 處理的是「卡已經在
Pi 上」之後的事——找到它、連進去、看畫面、換系統。網路開機安裝（netboot）的相關
專案可以參考 [pipxe](https://github.com/ipxe/pipxe)、
[rpi-pxe-server](https://github.com/beta-tester/install-pxe-server)，
這部分 piscout 還在規劃中。

## 常見問題

**Windows 上怎麼找到區網裡樹莓派的 IP？**
打開 piscout 就會自動掃描 /24 網段，用 MAC 前綴與 mDNS 名稱標出樹莓派。

**能在同一個程式裡開 SSH 終端機和遠端桌面嗎？**
可以。登入後終端機（xterm.js）和桌面（noVNC，走 SSH 通道）是同一個視窗的分頁。
遠端桌面需要 Raspberry Pi OS 桌面版（Wayland / wayvnc），Lite 沒有桌面。

**不拔 SD 卡可以重灌系統嗎？**
可以，前提是 Pi 還開得起來而且開著 SSH：piscout 會把官方映像經 SSH 串流寫進 Pi 自己的
開機磁碟，並在重新開機前校驗。**從未開機過的空白卡做不到**，那種卡請先在電腦上燒一次。

**它怎麼決定要裝哪個系統？**
登入後讀取 `/proc/device-tree/model` 得知型號，挑對應的官方映像：Pi 3 以後建議 64 位元桌面版，
更舊的板子用 32 位元版，選精簡用途就推薦 Lite。板子跑不起來的映像會直接拒絕。

**能取代 Raspberry Pi Imager 嗎？**
不能。Imager 負責把卡寫好；piscout 負責卡已經在 Pi 上之後的管理，也附了方便的本機燒錄。

**支援 Linux / macOS 嗎？**
目前只支援 Windows（含本機燒錄）。掃描、終端機、遠端重灌都是純 Python，之後可以移植。

## 從原始碼執行

需要 Python 3.9 以上、Windows 10/11（需要 WebView2，Win11 內建）。

```bash
git clone https://github.com/<你的帳號>/piscout.git
cd piscout
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run_gui.py
```

寫入本機磁碟需要系統管理員權限，請用系統管理員身分開啟終端機。

打包成 exe：

```bash
pip install pyinstaller
build.bat
```

## 專案結構

```
run_gui.py            # 桌面版入口
build.bat             # PyInstaller 打包
piscout/
├── gui.py            # 原生視窗（pywebview）+ 只聽 127.0.0.1 的本機服務
├── app.py            # FastAPI：API、終端機與桌面的 WebSocket
├── scanner.py        # 區網掃描、ARP 解析、mDNS
├── remote.py         # SSH 連線、啟動遠端桌面、安裝 agent
├── remoteflash.py    # 遠端重灌
├── flasher.py        # 映像清單、型號建議、本機燒錄、開機設定
├── agent/agent.py    # 會被推到 Pi 上的小程式（只用標準函式庫）
└── static/           # 介面；vendor/ 內是 xterm.js 與 noVNC
tests/
```

跑測試：`pytest`

## 注意事項

- 介面服務只綁 `127.0.0.1`，並使用一次性 token 建立終端機/桌面連線
- SSH 的 host key 目前是「第一次連線就接受」，家用網路還好，正式環境請自己改
  （`remote.py` 的 `AutoAddPolicy`）
- 遠端桌面會在 Pi 上開一個**無密碼、只聽本機**的 VNC，因為只能經由 SSH 通道連到，
  所以安全性等同 SSH；關閉連線時會把它停掉
- 開機設定裡的密碼只寫雜湊值；Wi-Fi 密碼因為格式限制會以明文寫在 boot 分割區
- API 只接受私有網段的 IP；映像只下載樹莓派官方網域
- 只掃自己的網路

## 驗證狀況與還沒做的

已實測：區網掃描與 Pi 辨識、內建終端機（含縮放）、映像預處理與開機設定寫入、
Pi 端寫入腳本的流程與校驗邏輯（用本機模擬）、單元測試。

**還沒在真機上實測**：遠端重灌的實際寫入、遠端桌面、本機 SD 卡燒錄。
Pi 專屬的部分（記憶體內執行環境、sysrq 重開機、wayvnc）是依文件寫的，
第一次實機測試很可能需要微調。

- [ ] 實機驗證以上三項，並補上各型號的測試結果
- [ ] 遠端桌面支援 X11 / RealVNC 的舊系統
- [ ] 儲存已知裝置、SSH key 登入的介面
- [ ] 多台 Pi 總覽頁
- [ ] Linux / macOS 的本機燒錄
- [ ] 空白 Pi 用 PXE / 網路開機安裝

## 已知問題

- Windows 防火牆有時會擋掉 mDNS，主機名稱會是空的，但 IP 與 MAC 判斷正常
- 掃描只做 IPv4，而且只掃 /24
- 用了 USB 網卡等非原廠網卡，MAC 前綴會對不上
- 本機燒錄後 Windows 可能會跳出「需要格式化磁碟」，**不要格式化**，直接關掉

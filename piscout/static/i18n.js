/* 介面語言：自動偵測，也可以手動切換。
 *
 * 介面文字原本就是用繁體中文寫的，英文版是在畫面上把中文換成英文：
 *   EXACT  整段文字完全相同才換（短詞用，避免誤傷）
 *   SUB    文字中出現就換（長句與固定片語，由長到短）
 *   RX     含數字或變數的句型
 * 後端回傳的錯誤訊息已經依 X-Lang 翻好，不會經過這裡。
 */
(function () {
  const saved = (() => { try { return localStorage.getItem('piscout_lang'); } catch (e) { return null; } })();
  const nav = (navigator.languages && navigator.languages[0]) || navigator.language || 'en';
  const lang = saved || (/^zh/i.test(nav) ? 'zh' : 'en');
  window.PISCOUT_LANG = lang;
  document.documentElement.lang = lang === 'zh' ? 'zh-Hant' : 'en';

  window.setLang = function (l) {
    try { localStorage.setItem('piscout_lang', l); } catch (e) {}
    location.reload();
  };

  const EXACT = {
    '裝置': 'Devices', '執行': 'Run', '總覽': 'Overview', '燒錄系統': 'Flash OS',
    '連線': 'Connect', '收起': 'Collapse', '重灌系統': 'Re-image',
    '終端機': 'Terminal', '遠端桌面': 'Remote desktop', '系統資訊': 'System info',
    '關閉連線': 'Close', '重新掃描': 'Rescan', '重新整理': 'Refresh',
    '型號': 'Model', '系統': 'OS', '主機名稱': 'Hostname', '開機時間': 'Uptime',
    'CPU 溫度': 'CPU temp', '負載': 'Load', '記憶體': 'Memory', '磁碟': 'Disk',
    '使用者名稱': 'Username', '密碼': 'Password', '新密碼': 'New password',
    '樹莓派': 'Raspberry Pi', '用途': 'Purpose', '時區': 'Time zone',
    '鍵盤配置': 'Keyboard layout', '開始燒錄': 'Start flashing',
    '安裝 agent': 'Install agent', '安裝中…': 'Installing…', '讀取中…': 'Loading…',
    '連線中…': 'Connecting…', '掃描中…': 'Scanning…', '載入失敗': 'Failed to load',
    'SSH 開啟': 'SSH on', 'SSH 未開': 'SSH off',
    '名稱': 'Name', '狀態': 'Status', '溫度': 'Temp', '來源': 'Source',
    '在線': 'Online', '離線': 'Offline', '無帳密': 'No login',
    '重新開機': 'Reboot', '關機': 'Shut down', '更新套件': 'Update packages',
    '自動更新': 'Auto refresh', '全選': 'Select all',
  };

  const SUB = [
    ['啟動中，正在掃描區網…', 'Starting… scanning the network'],
    ['正在掃描區網…', 'Scanning the network…'],
    ['清除已存帳密', 'Forget saved logins'],
    ['清除這台電腦上儲存的所有樹莓派帳號密碼', 'Remove all Raspberry Pi logins saved on this computer'],
    ['要清除這台電腦上儲存的所有樹莓派帳號密碼嗎？', 'Remove all Raspberry Pi logins saved on this computer?'],
    ['顯示非樹莓派', 'Show non-Pi devices'],
    ['1. 要重灌哪一台？', '1. Which one to re-image?'],
    ['區網裡的樹莓派（SD 卡留在 Pi 上，從這裡遠端重灌）',
      'A Raspberry Pi on the network (SD card stays in the Pi; re-image remotely)'],
    ['插在這台電腦上的 SD 卡', 'An SD card inserted in this computer'],
    ['目前的登入帳號', 'Current login username'],
    ['目前的登入密碼（也用來 sudo）', 'Current login password (also used for sudo)'],
    ['讀取這台的型號與系統', "Read this Pi's model and OS"],
    ['必須是還開得起來、而且開著 SSH 的樹莓派。完全空白的 SD 卡在網路上看不到， 請改選「插在這台電腦上的 SD 卡」。重灌會清空這台 Pi 的所有資料。',
      'The Pi must still boot and have SSH enabled. A completely blank SD card cannot be seen on the network; choose "An SD card inserted in this computer" instead. Re-imaging erases everything on the Pi.'],
    ['2. 這是哪一款樹莓派？', '2. Which Raspberry Pi model is it?'],
    ['型號（印在板子上）', 'Model (printed on the board)'],
    ['桌面版：有畫面，可遠端操作桌面', 'Desktop: with GUI, remote desktop works'],
    ['精簡版：只用終端機，省資源', 'Lite: terminal only, saves resources'],
    ['連線並勾選「記住」一次，之後這裡會自動顯示。', 'Connect once and tick "Remember"; this will then fill in automatically.'],
    ['帳密沒能存起來：', 'Could not save the login: '],
    ['連線後會自動安裝 agent', 'The agent is installed automatically after you connect'],
    ['先連線到樹莓派，再把檔案拖進來', 'Connect to a Raspberry Pi first, then drop files here'],
    ['放開以傳到樹莓派的桌面', 'Release to send to the Pi desktop'],
    ['放開以傳到終端機目前所在的資料夾', "Release to send to the terminal's current folder"],
    ['不支援資料夾，請先壓縮成 zip 再傳', 'Folders are not supported; zip it first'],
    ['準備傳送…', 'Preparing…'],
    ['目標資料夾：', 'Target folder: '],
    ['先顯示上次的樹莓派，正在背景重新掃描…', 'Showing the Pis from last time while scanning in the background…'],
    ['這次沒掃到', 'Not found this time'],
    ['上次記錄', 'From last time'],
    ['進階：遠端重灌（有風險）', 'Advanced: remote re-imaging (risky)'],
    ['更多系統選項（桌面或精簡版、換版本）', 'More OS options (Desktop or Lite, other versions)'],
    ['3. 重灌後的開機設定', '3. Boot settings after re-imaging'],
    ['更多設定（主機名稱、國碼、時區、鍵盤、校驗）', 'More settings (hostname, country, timezone, keyboard, verify)'],
    ['Wi-Fi 名稱（有接網路線可留空）', 'Wi-Fi name (leave empty if using Ethernet)'],
    ['Wi-Fi 密碼', 'Wi-Fi password'],
    ['Wi-Fi 國碼', 'Wi-Fi country code'],
    ['本機燒錄時，寫完後讀回校驗', 'When flashing locally, verify by reading back'],
    ['SSH 一律會啟用。系統映像全部來自樹莓派官方網站。遠端重灌一定會校驗。',
      'SSH is always enabled. All OS images come from the official Raspberry Pi website. Remote re-imaging is always verified.'],
    ['沒有找到樹莓派，可以勾「顯示非樹莓派」看看其他設備。',
      'No Raspberry Pi found. Tick "Show non-Pi devices" to see everything else.'],
    ['這台樹莓派 SSH 沒有開，沒辦法遠端操作。可能還沒有系統，或沒啟用 SSH。',
      "This Pi's SSH is off, so it cannot be controlled remotely. It may have no system yet, or SSH is not enabled."],
    ['可以把 SD 卡拿下來插到這台電腦，用「燒錄系統」重新燒錄。',
      'Take the SD card out, put it in this computer and use "Flash OS".'],
    [' · 新款樹莓派（登入後可確認型號）', ' · Newer Raspberry Pi (log in to confirm the model)'],
    ['記住這台的帳號密碼', 'Remember this login'],
    ['密碼會用 Windows 的使用者金鑰加密後存在這台電腦，換電腦或換帳號就解不開。',
      'The password is encrypted with your Windows user key and stored on this computer; it cannot be decrypted on another PC or account.'],
    ['掃描失敗：', 'Scan failed: '],
    ['正在啟動遠端桌面…（第一次會需要幾秒）', 'Starting remote desktop… (the first time takes a few seconds)'],
    ['遠端桌面已中斷。', 'Remote desktop disconnected.'],
    ['遠端桌面連線失敗或中斷。', 'Remote desktop connection failed or was interrupted.'],
    ['agent 已在執行', 'agent is running'],
    ['（已自動套用對應的建議）', ' (matching recommendation applied)'],
    ['看起來是新款樹莓派。填入帳密後會自動讀取確切型號。',
      'Looks like a newer Raspberry Pi. Enter the login and the exact model is read automatically.'],
    ['填入帳密後會自動讀取型號；也可以自己在下面選。',
      'Enter the login to read the model automatically, or choose it below.'],
    ['還沒有掃描到樹莓派', 'No Raspberry Pi found yet'],
    [' · SSH 未開', ' · SSH off'],
    ['請先選一台樹莓派', 'Please choose a Raspberry Pi first'],
    ['讀取型號中…', 'Reading the model…'],
    ['型號未知', 'Unknown model'],
    ['，請自己選型號', ', please choose the model yourself'],
    ['★ 推薦：', '★ Recommended: '],
    ['（此型號不支援）', ' (not supported by this model)'],
    ['最佳建議：', 'Best choice: '],
    [' · 空白', ' · blank'],
    [' · 已有樹莓派系統', ' · has Raspberry Pi OS'],
    [' · 無法辨識', ' · unrecognized'],
    ['未命名', 'unnamed'],
    ['沒有偵測到可移除的磁碟，請插入 SD 卡', 'No removable disk detected. Insert an SD card.'],
    ['目前不是系統管理員身分，可以先設定，但寫入時會失敗。請用「以系統管理員身分執行」開啟。',
      'Not running as administrator. You can set things up, but writing will fail. Start the app with "Run as administrator".'],
    ['只列出 USB / SD 類的可移除磁碟，不會列出系統碟。',
      'Only removable USB / SD disks are listed, never the system disk.'],
    ['請先選好系統', 'Please choose an OS first'],
    ['請設定新密碼，不然重灌之後登不進去', 'Please set a new password, or you cannot log in after re-imaging'],
    ['請填目前的登入帳號', 'Please enter the current login username'],
    ['請先選好 SD 卡', 'Please choose an SD card first'],
    ['寫入並校驗完成，樹莓派正在重新開機。開機後我會自動掃描，找到就回到裝置頁。',
      'Written and verified. The Pi is rebooting; I will scan automatically and return to Devices when it is back.'],
    ['燒錄完成。把 SD 卡插進樹莓派開機，等一到兩分鐘，我會自動重新掃描。',
      'Flashing finished. Put the SD card into the Pi and boot it; I will rescan automatically in a minute or two.'],
    ['連線已結束', 'connection closed'],
    ['以系統管理員身分重新啟動', 'Restart as administrator'],
    ['正在以系統管理員身分重新啟動…', 'Restarting as administrator…'],
    ['寫入 SD 卡需要系統管理員權限。其他功能（掃描、終端機、遠端桌面）不需要。',
      'Writing to an SD card needs administrator rights. Scanning, the terminal and remote desktop do not.'],
    ['插在這台電腦上的 SD 卡（建議）', 'An SD card inserted in this computer (recommended)'],
    ['· 進階功能，預設關閉', '· advanced feature, off by default'],
    ['啟用進階功能：遠端重灌（有風險）', 'Enable advanced feature: remote re-imaging (risky)'],
    ['遠端重灌是在「執行中」的樹莓派上覆寫它自己的 SD 卡。如果中途關閉程式、斷電、 斷網或電腦睡眠，那張卡會變成寫了一半、開不了機，而且無法從遠端修復，只能把卡拿到電腦上重燒。 請先準備讀卡機或備用的 SD 卡。',
      'Remote re-imaging overwrites the SD card of a Pi that is running. If the app is closed, power or the network drops, or the computer sleeps midway, the card ends up half-written and the Pi will not boot. It cannot be repaired remotely; the card has to be re-flashed from a computer. Prepare a card reader or a spare SD card first.'],
    ['遠端重灌是進階功能，請先啟用上方的「進階功能」並確認風險。',
      'Remote re-imaging is an advanced feature. Enable it above and confirm the risk first.'],
    ['我有讀卡機或備用的 SD 卡，萬一中途失敗可以用電腦重燒這張卡',
      'I have a card reader or a spare SD card, so I can re-flash this card from a computer if it fails midway'],
    ['遠端重灌失敗時，這張卡需要用電腦重燒。請先勾選上方的確認。',
      'If remote re-imaging fails, this card must be re-flashed from a computer. Please tick the confirmation above first.'],
    ['這張卡現在只寫了一半，樹莓派開不了機。請把卡拿到電腦上，到「燒錄系統」選「插在這台電腦上的 SD 卡」重新燒錄。',
      'This card is now half-written and the Pi cannot boot. Take the card to a computer, open "Flash OS", choose "An SD card inserted in this computer" and flash it again.'],
    // 總覽
    ['還沒有樹莓派。先到「裝置」掃描並連線一次，讓我記住帳密。',
      'No Raspberry Pi yet. Scan and connect once on the "Devices" tab so I can remember the login.'],
    ['沒有儲存帳密', 'No saved login'],
    ['先到「裝置」連線一次並勾選「記住」，這裡才能顯示狀態。',
      'Connect once on "Devices" with "Remember" ticked so the status can be shown here.'],
    ['批次操作會對勾選的樹莓派使用已儲存的帳密。', 'Batch actions use the saved login of each selected Pi.'],
    ['健康檢查', 'Health check'], ['快速設定', 'Quick setup'], ['正在檢查…', 'Checking…'],
    ['重新檢查', 'Check again'], ['✔ 已完成', '✔ Done'], ['已執行', 'Applied'], ['執行中…', 'Working…'],
    ['需要重開機才會生效', 'A reboot is needed to take effect'],
  ];
  SUB.sort((a, b) => b[0].length - a[0].length);

  const RX = [
    [/^(.*) · 找到 (\d+) 台設備，(\d+) 台是樹莓派(。如果你的樹莓派還沒有系統.*)?$/,
      (m, net, n, pis, tail) => `${net} · Found ${n} device(s), ${pis} Raspberry Pi(s)` +
        (tail ? '. If your Pi has no system yet, put its SD card into this computer and I will flash it for you.' : '')],
    [/下載約 (.+?)，寫入後 (.+?) · 來源：樹莓派官方網站/,
      (m, a, b) => `download ≈ ${a}, ${b} after writing · source: official Raspberry Pi website`],
    [/磁碟 (\d+)/, (m, n) => `Disk ${n}`],
    [/^確定清除 (\S+) 並重灌$/, (m, ip) => `Wipe ${ip} and re-image`],
    [/^確定清除磁碟 (\d+) 並燒錄$/, (m, n) => `Wipe disk ${n} and flash`],
    [/^(\S+) 上的所有資料都會被刪除！過程中請不要斷電或斷網，約需 10–30 分鐘。$/,
      (m, ip) => `All data on ${ip} will be erased! Do not power off or disconnect during the process. About 10–30 minutes.`],
    [/^(.*) 上的所有資料都會被刪除！$/, (m, d) => `All data on ${d} will be erased!`],
    [/(\d+) 天 (\d+) 小時 (\d+) 分/, (m, d, h, mi) => `${d}d ${h}h ${mi}m`],
    [/(\d+) 小時 (\d+) 分/, (m, h, mi) => `${h}h ${mi}m`],
    [/^已選 (\d+) 台$/, (m, n) => `${n} selected`],
    [/^完成：(\d+) 台成功，(\d+) 台失敗$/, (m, a, b) => `Done: ${a} succeeded, ${b} failed`],
    [/^確定要對 (\d+) 台執行「(.+)」嗎？$/, (m, n, a) => `Run "${trText(a)}" on ${n} device(s)?`],
  ];

  function trText(s) {
    if (lang !== 'en') return s;
    const norm = s.replace(/\s+/g, ' ').trim();
    if (!/[一-鿿]/.test(norm)) return s;
    let out = norm;
    if (Object.prototype.hasOwnProperty.call(EXACT, out)) {
      out = EXACT[out];
    } else {
      for (const [re, fn] of RX) {
        if (re.test(out)) { out = out.replace(re, fn); }
      }
      for (const [zh, en] of SUB) {
        if (out.includes(zh)) out = out.split(zh).join(en);
      }
    }
    const lead = s.match(/^\s*/)[0], trail = s.match(/\s*$/)[0];
    return lead + out + trail;
  }
  window.t = trText;

  if (lang !== 'en') return;

  function walk(node) {
    if (node.nodeType === 3) {
      const v = trText(node.nodeValue);
      if (v !== node.nodeValue) node.nodeValue = v;
      return;
    }
    if (node.nodeType !== 1) return;
    if (node.tagName === 'SCRIPT' || node.tagName === 'STYLE') return;
    for (const a of ['placeholder', 'title']) {
      if (node.hasAttribute && node.hasAttribute(a)) {
        const v = trText(node.getAttribute(a));
        if (v !== node.getAttribute(a)) node.setAttribute(a, v);
      }
    }
    for (const c of node.childNodes) walk(c);
  }

  function start() {
    walk(document.body);
    new MutationObserver(muts => {
      for (const m of muts) {
        if (m.type === 'characterData') walk(m.target);
        else if (m.type === 'attributes') walk(m.target);
        else m.addedNodes.forEach(walk);
      }
    }).observe(document.body, {
      subtree: true, childList: true, characterData: true,
      attributes: true, attributeFilter: ['placeholder', 'title'],
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();

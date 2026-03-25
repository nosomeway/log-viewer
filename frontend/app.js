const fileListEl = document.getElementById("file-list");
const listErrorEl = document.getElementById("list-error");
const logBodyEl = document.getElementById("log-body");
const logMetaEl = document.getElementById("log-meta");
const logErrorEl = document.getElementById("log-error");
const tailInput = document.getElementById("tail-lines");
const offsetInput = document.getElementById("page-offset");
const limitInput = document.getElementById("page-limit");
const btnRefresh = document.getElementById("btn-refresh");

let selectedPath = null;

function pageParams() {
  const off = offsetInput.value.trim();
  const lim = limitInput.value.trim();
  if (off === "" && lim === "") return null;
  const o = Number(off);
  const l = Number(lim);
  if (Number.isInteger(o) && o >= 0 && Number.isInteger(l) && l >= 1) {
    return { offset: o, limit: l };
  }
  return "invalid";
}

async function loadFiles() {
  listErrorEl.hidden = true;
  fileListEl.innerHTML = "";
  try {
    const res = await fetch("/api/files");
    if (!res.ok) throw new Error(await res.text());
    const files = await res.json();
    if (!files.length) {
      fileListEl.innerHTML = "<li class=\"empty\">暂无日志文件（请在 logs 目录放入 .log 等文件）</li>";
      return;
    }
    for (const f of files) {
      const li = document.createElement("li");
      const a = document.createElement("button");
      a.type = "button";
      a.className = "file-link";
      a.textContent = f.path;
      a.addEventListener("click", () => {
        selectedPath = f.path;
        document.querySelectorAll(".file-link").forEach((el) => el.classList.remove("active"));
        a.classList.add("active");
        loadLog();
      });
      li.appendChild(a);
      fileListEl.appendChild(li);
    }
  } catch (e) {
    listErrorEl.textContent = e.message || String(e);
    listErrorEl.hidden = false;
  }
}

async function loadLog() {
  logErrorEl.hidden = true;
  logMetaEl.hidden = true;
  logBodyEl.textContent = "";
  if (!selectedPath) return;

  const pp = pageParams();
  if (pp === "invalid") {
    logErrorEl.textContent = "分页时请同时填写有效的 offset（整数≥0）与 limit（整数≥1）。";
    logErrorEl.hidden = false;
    return;
  }

  let url = `/api/logs/${encodeURI(selectedPath)}`;
  if (pp) {
    url += `?offset=${pp.offset}&limit=${pp.limit}`;
  } else {
    const tail = Math.min(50000, Math.max(1, Number(tailInput.value) || 500));
    url += `?tail=${tail}`;
  }

  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    logBodyEl.textContent = data.lines.join("\n");
    const parts = [];
    if (data.encoding) parts.push(`编码: ${data.encoding}`);
    if (data.mode === "page") {
      parts.push(`分页 offset=${data.offset} limit=${data.limit}，本段共 ${data.total_lines_in_chunk} 行`);
    } else {
      parts.push(`末尾 ${data.tail} 行`);
    }
    if (data.truncated) {
      parts.push("（已按 LOG_MAX_READ_BYTES 截断字节后再解码分行）");
    }
    logMetaEl.textContent = parts.join(" · ");
    logMetaEl.hidden = false;
  } catch (e) {
    logErrorEl.textContent = e.message || String(e);
    logErrorEl.hidden = false;
  }
}

btnRefresh.addEventListener("click", loadLog);
tailInput.addEventListener("change", () => {
  if (selectedPath) loadLog();
});
[offsetInput, limitInput].forEach((el) => {
  el.addEventListener("change", () => {
    if (selectedPath) loadLog();
  });
});

loadFiles();

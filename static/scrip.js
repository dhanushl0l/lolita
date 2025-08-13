const chatBox = document.getElementById('chat-box');
const input = document.getElementById('msg-input');
const sendBtn = document.getElementById('send-btn');
const headerBar = document.getElementById('chat-header');

let socket;
let firstMessageSent = false;
let currentBotMsg = null;
let botTyping = false;

document.addEventListener("DOMContentLoaded", () => {
    const getCookie = name =>
        document.cookie.split("; ").find(row => row.startsWith(name + "="))?.split("=")[1];

    const setCookie = (name, value, days = 365) => {
        const expires = new Date(Date.now() + days * 24 * 60 * 60 * 1000).toUTCString();
        document.cookie = `${name}=${value}; expires=${expires}; path=/`;
    };

    document.documentElement.setAttribute("data-theme", getCookie("theme") || "dark");

    const themeToggle = document.getElementById("theme-toggle");
    if (themeToggle) {
        themeToggle.addEventListener("click", () => {
            const current = document.documentElement.getAttribute("data-theme");
            const next = current === "light" ? "dark" : "light";
            document.documentElement.setAttribute("data-theme", next);
            setCookie("theme", next);
        });
    }
});


function addMessage(text, className, withCopyBtn = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message ' + className;
    msgDiv.textContent = text;

    if (withCopyBtn) {
        const copyBtn = document.createElement('button');
        copyBtn.textContent = 'Copy';
        copyBtn.className = 'copy-btn';
        copyBtn.title = 'Copy to clipboard';
        copyBtn.onclick = () => {
            navigator.clipboard.writeText(text).then(() => {
                copyBtn.textContent = 'Copied!';
                setTimeout(() => (copyBtn.textContent = 'Copy'), 1500);
            });
        };
        msgDiv.appendChild(copyBtn);
    }

    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    return msgDiv;
}

function setupSocket() {
    let protocol = (location.protocol === "https:") ? "wss://" : "ws://";
    socket = new WebSocket(`${protocol}${location.host}/ws/chat`);

    socket.addEventListener("message", (event) => {
        if (event.data === "[[END]]") {
            finishMessage(currentBotMsg);
            return;
        }
        botText += event.data;
        currentBotMsg.querySelector('.bot-text').textContent = botText;
        chatBox.scrollTop = chatBox.scrollHeight;
    });

    socket.addEventListener("close", () => console.log("WebSocket closed"));
    socket.addEventListener("error", (err) => console.error("WebSocket error", err));
}


function sendMessage() {
    if (botTyping) return;
    const message = input.value.trim();
    if (!message) return;
    if (!firstMessageSent) {
        chatBox.classList.remove("chat-box-empty");
        headerBar.classList.remove("chat-header-stock");
        document.querySelector('.chat-title').style.display = 'inline';
        document.querySelector('.chat-box-title').style.display = 'none';
        firstMessageSent = true;
    }

    addMessage(message, 'user-msg');
    input.value = '';
    botTyping = true;
    sendBtn.disabled = true;
    input.disabled = true;

    currentBotMsg = document.createElement('div');
    currentBotMsg.className = 'message bot-msg';
    currentBotMsg.innerHTML = `<span class="bot-text typing">${NAME} is typing<span class="dots"></span></span>`;
    chatBox.appendChild(currentBotMsg);
    chatBox.scrollTop = chatBox.scrollHeight;

    botText = '';

    if (!socket || socket.readyState !== WebSocket.OPEN) {
        setupSocket();
        socket.addEventListener("open", () => socket.send(message), { once: true });
    } else {
        socket.send(message);
    }
}

function finishMessage(botMsg) {
    const copyBtn = document.createElement('button');
    copyBtn.textContent = 'Copy';
    copyBtn.className = 'copy-btn';
    copyBtn.title = 'Copy to clipboard';
    copyBtn.onclick = () => {
        navigator.clipboard.writeText(botText).then(() => {
            copyBtn.textContent = 'Copied!';
            setTimeout(() => (copyBtn.textContent = 'Copy'), 1500);
        });
    };
    botMsg.appendChild(copyBtn);

    botTyping = false;
    sendBtn.disabled = false;
    input.disabled = false;
    input.focus();
}

sendBtn.addEventListener('click', sendMessage);

input.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

document.addEventListener('keydown', (e) => {
    if (e.ctrlKey || e.altKey || e.metaKey) return;
    if (e.key.length === 1) {
        e.preventDefault();
        input.focus();
        const start = input.selectionStart || input.value.length;
        const end = input.selectionEnd || input.value.length;
        input.value =
            input.value.substring(0, start) + e.key + input.value.substring(end);
        input.setSelectionRange(start + 1, start + 1);
    }
});

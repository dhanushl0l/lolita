const chatBox = document.getElementById('chat-box');
const input = document.getElementById('msg-input');
const sendBtn = document.getElementById('send-btn');

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

function botReply(sentence) {
    botTyping = true;
    sendBtn.disabled = true;
    input.disabled = true;

    const words = sentence.split(' ');
    let index = 0;
    let currentText = '';
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message bot-msg';
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    function typeWord() {
        if (index < words.length) {
            currentText += (index === 0 ? '' : ' ') + words[index];
            msgDiv.textContent = currentText;
            chatBox.scrollTop = chatBox.scrollHeight;
            index++;
            setTimeout(typeWord, 400);
        } else {
            const copyBtn = document.createElement('button');
            copyBtn.textContent = 'Copy';
            copyBtn.className = 'copy-btn';
            copyBtn.title = 'Copy to clipboard';
            copyBtn.onclick = () => {
                navigator.clipboard.writeText(currentText).then(() => {
                    copyBtn.textContent = 'Copied!';
                    setTimeout(() => (copyBtn.textContent = 'Copy'), 1500);
                });
            };
            msgDiv.appendChild(copyBtn);
            botTyping = false;
            sendBtn.disabled = false;
            input.disabled = false;
            input.focus();
        }
    }
    typeWord();
}

let firstMessageSent = false;

function sendMessage() {
    if (botTyping) return;
    const message = input.value.trim();
    if (!message) return;
    if (!firstMessageSent) {
        chatBox.classList.remove("chat-box-empty");
        document.querySelector('.chat-title').style.display = 'inline';
        document.querySelector('.chat-box-title').style.display = 'none';
        firstMessageSent = true;
    }

    addMessage(message, 'user-msg');
    input.value = '';
    botTyping = true;
    sendBtn.disabled = true;
    input.disabled = true;

    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-msg typing-indicator';
    typingDiv.innerHTML = `${NAME} is typing<span class="typing-dots"></span>`;
    chatBox.appendChild(typingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
    }).then(response => {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let botText = '';
        chatBox.removeChild(typingDiv);

        const msgDiv = document.createElement('div');
        msgDiv.className = 'message bot-msg';
        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;

        let buffer = '';
        function read() {
            reader.read().then(({ done, value }) => {
                if (done) {
                    finishMessage();
                    return;
                }
                buffer += decoder.decode(value, { stream: true });
                let boundary;
                while ((boundary = buffer.indexOf('\n\n')) !== -1) {
                    const fullChunk = buffer.slice(0, boundary);
                    buffer = buffer.slice(boundary + 2);

                    if (fullChunk.startsWith('data: ')) {
                        const token = fullChunk.slice(6);
                        botText += token;
                        msgDiv.textContent = botText;
                        chatBox.scrollTop = chatBox.scrollHeight;
                    }
                }
                read();
            });
        }

        function finishMessage() {
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
            msgDiv.appendChild(copyBtn);

            botTyping = false;
            sendBtn.disabled = false;
            input.disabled = false;
            input.focus();
        }
        read();
    });
}


sendBtn.addEventListener('click', sendMessage);

input.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

const chatBox = document.getElementById('chat-box');
const input = document.getElementById('msg-input');
const sendBtn = document.getElementById('send-btn');
const themeToggle = document.getElementById('theme-toggle');

let botTyping = false;

document.addEventListener("DOMContentLoaded", () => {
    const themeToggle = document.getElementById("theme-toggle");
    const savedTheme = localStorage.getItem("theme") || "light";
    document.documentElement.setAttribute("data-theme", savedTheme);

    themeToggle.addEventListener("click", () => {
        const current = document.documentElement.getAttribute("data-theme");
        const next = current === "light" ? "dark" : "light";
        document.documentElement.setAttribute("data-theme", next);
        localStorage.setItem("theme", next);
    });
});


themeToggle.addEventListener('click', () => {
    document.body.classList.toggle('dark');
    if (document.body.classList.contains('dark')) {
        themeToggle.textContent = 'Light Mode';
    } else {
        themeToggle.textContent = 'Dark Mode';
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

function sendMessage() {
    if (botTyping) return;
    const message = input.value.trim();
    if (!message) return;
    addMessage(message, 'user-msg');
    input.value = '';

    botTyping = true;
    sendBtn.disabled = true;
    input.disabled = true;

    const msgDiv = document.createElement('div');
    msgDiv.className = 'message bot-msg';
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
    }).then(response => {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let botText = '';

        function read() {
            reader.read().then(({ done, value }) => {
                if (done) {
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
                    return;
                }
                const chunk = decoder.decode(value, { stream: true });
                const matches = chunk.match(/data: (.*)\n\n/);
                if (matches) {
                    const token = matches[1];
                    botText += token;
                    msgDiv.textContent = botText;
                    chatBox.scrollTop = chatBox.scrollHeight;
                }
                read();
            });
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

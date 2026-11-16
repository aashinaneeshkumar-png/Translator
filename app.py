from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Language Voice Translator</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f0f2f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.1);
            width: 90%;
            max-width: 650px;
        }
        h1 {
            text-align: center;
            color: #1a202c;
            margin-top: 0;
            font-size: 24px;
        }
        .controls {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
        }
        select {
            flex: 1;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #cbd5e0;
            font-size: 15px;
            background: #f8fafc;
        }
        .swap-btn {
            background: #edf2f7;
            border: 1px solid #cbd5e0;
            border-radius: 8px;
            padding: 8px 14px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
        }
        .swap-btn:hover { background: #e2e8f0; }
        .status {
            text-align: center;
            font-size: 14px;
            color: #4a5568;
            margin-bottom: 15px;
            min-height: 20px;
            font-weight: 500;
        }
        label {
            font-weight: 600;
            color: #2d3748;
            display: block;
            margin-bottom: 6px;
        }
        textarea {
            width: 100%;
            height: 110px;
            padding: 12px;
            border-radius: 10px;
            border: 1px solid #cbd5e0;
            font-size: 16px;
            resize: vertical;
            box-sizing: border-box;
            margin-bottom: 15px;
            background: #f8fafc;
        }
        .btn-group {
            display: flex;
            gap: 10px;
            justify-content: center;
        }
        button.action-btn {
            padding: 12px 20px;
            border: none;
            border-radius: 10px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            color: white;
            transition: opacity 0.2s;
        }
        button.action-btn:disabled {
            background-color: #a0aec0 !important;
            cursor: not-allowed;
        }
        #startBtn { background-color: #3182ce; }
        #stopBtn { background-color: #e53e3e; }
        #clearBtn { background-color: #718096; }
    </style>
</head>
<body>

<div class="container">
    <h1>🌍 Multi-Language Voice Translator</h1>
    
    <div class="controls">
        <select id="srcLang">
            <option value="hi-IN|hi" selected>Hindi</option>
            <option value="en-US|en">English</option>
            <option value="ml-IN|ml">Malayalam</option>
            <option value="ta-IN|ta">Tamil</option>
            <option value="te-IN|te">Telugu</option>
            <option value="kn-IN|kn">Kannada</option>
            <option value="bn-IN|bn">Bengali</option>
            <option value="mr-IN|mr">Marathi</option>
            <option value="es-ES|es">Spanish</option>
            <option value="fr-FR|fr">French</option>
            <option value="de-DE|de">German</option>
            <option value="ar-SA|ar">Arabic</option>
            <option value="ja-JP|ja">Japanese</option>
            <option value="ko-KR|ko">Korean</option>
        </select>

        <button class="swap-btn" onclick="swapLanguages()">⇄</button>

        <select id="tgtLang">
            <option value="en-US|en" selected>English</option>
            <option value="hi-IN|hi">Hindi</option>
            <option value="ml-IN|ml">Malayalam</option>
            <option value="ta-IN|ta">Tamil</option>
            <option value="te-IN|te">Telugu</option>
            <option value="kn-IN|kn">Kannada</option>
            <option value="bn-IN|bn">Bengali</option>
            <option value="mr-IN|mr">Marathi</option>
            <option value="es-ES|es">Spanish</option>
            <option value="fr-FR|fr">French</option>
            <option value="de-DE|de">German</option>
            <option value="ar-SA|ar">Arabic</option>
            <option value="ja-JP|ja">Japanese</option>
            <option value="ko-KR|ko">Korean</option>
        </select>
    </div>

    <div class="status" id="status">Click "Start Speaking", talk, then click "Stop & Translate"</div>

    <label>📝 What you said:</label>
    <textarea id="inputBox" readonly placeholder="Your spoken text will appear here..."></textarea>

    <label>💡 Translated Output:</label>
    <textarea id="outputBox" readonly placeholder="Translation will appear here..."></textarea>

    <div class="btn-group">
        <button id="startBtn" class="action-btn" onclick="startListening()">🎤 Start Speaking</button>
        <button id="stopBtn" class="action-btn" onclick="stopListening()" disabled>⏹️ Stop & Translate</button>
        <button id="clearBtn" class="action-btn" onclick="clearText()">🗑️ Clear</button>
    </div>
</div>

<script>
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition;
    let finalTranscript = "";
    let isRecording = false;

    if (!SpeechRecognition) {
        document.getElementById("status").innerText = "❌ Your browser doesn't support Speech Recognition. Please use Google Chrome or Microsoft Edge.";
        document.getElementById("startBtn").disabled = true;
    } else {
        recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;

        recognition.onresult = (event) => {
            let interim = "";
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript + " ";
                } else {
                    interim += event.results[i][0].transcript;
                }
            }
            document.getElementById("status").innerText = "🎙️ Hearing: " + (finalTranscript + interim);
        };

        recognition.onerror = (event) => {
            document.getElementById("status").innerText = "❌ Mic Error: " + event.error;
            resetButtons();
        };

        recognition.onend = () => {
            if (isRecording) {
                recognition.start();
            } else if (finalTranscript.trim().length > 0) {
                translateText(finalTranscript.trim());
            } else {
                document.getElementById("status").innerText = "⚠️ Nothing heard. Try speaking again.";
                resetButtons();
            }
        };
    }

    function startListening() {
        finalTranscript = "";
        isRecording = true;
        const srcFull = document.getElementById("srcLang").value;
        recognition.lang = srcFull.split("|")[0];
        
        document.getElementById("startBtn").disabled = true;
        document.getElementById("stopBtn").disabled = false;
        document.getElementById("status").innerText = "🎙️ Listening... Speak now!";
        recognition.start();
    }

    function stopListening() {
        isRecording = false;
        document.getElementById("stopBtn").disabled = true;
        document.getElementById("status").innerText = "🔄 Translating...";
        recognition.stop();
    }

    async function translateText(text) {
        const srcSelect = document.getElementById("srcLang");
        const tgtSelect = document.getElementById("tgtLang");
        const [srcSr, srcCode] = srcSelect.value.split("|");
        const [tgtSr, tgtCode] = tgtSelect.value.split("|");
        const srcName = srcSelect.options[srcSelect.selectedIndex].text;
        const tgtName = tgtSelect.options[tgtSelect.selectedIndex].text;

        appendBox("inputBox", `[${srcName}]: ${text}`);

        try {
            let translatedText = "";

            if (srcCode === tgtCode) {
                translatedText = text;
            } else {
                // 1. Try our Python backend first
                const response = await fetch("/translate", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ text, srcCode, tgtCode })
                });
                const data = await response.json();

                if (data.translation) {
                    translatedText = data.translation;
                } else {
                    // 2. Fallback: Fetch directly from user's browser (bypasses Render's shared IP limits)
                    const mmRes = await fetch(`https://api.mymemory.translated.net/get?q=${encodeURIComponent(text)}&langpair=${srcCode}|${tgtCode}`);
                    const mmData = await mmRes.json();
                    if (mmData.responseData && mmData.responseData.translatedText) {
                        translatedText = mmData.responseData.translatedText;
                    } else {
                        throw new Error("All translation services are currently busy.");
                    }
                }
            }

            appendBox("outputBox", `[${tgtName}]: ${translatedText}`);
            document.getElementById("status").innerText = "🔊 Speaking translation...";
            speakOutLoud(translatedText, tgtSr);
        } catch (err) {
            document.getElementById("status").innerText = "❌ Translation Error: " + err.message;
        } finally {
            resetButtons();
        }
    }

    function speakOutLoud(text, langTag) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = langTag;
        utterance.rate = 0.95;
        utterance.onend = () => {
            document.getElementById("status").innerText = "✅ Done! Ready for next sentence.";
        };
        window.speechSynthesis.speak(utterance);
    }

    function appendBox(id, text) {
        const box = document.getElementById(id);
        box.value = box.value ? box.value + "\\n----------------------------------------\\n" + text : text;
        box.scrollTop = box.scrollHeight;
    }

    function swapLanguages() {
        const src = document.getElementById("srcLang");
        const tgt = document.getElementById("tgtLang");
        const temp = src.value;
        src.value = tgt.value;
        tgt.value = temp;
    }

    function clearText() {
        document.getElementById("inputBox").value = "";
        document.getElementById("outputBox").value = "";
        document.getElementById("status").innerText = "Cleared! Ready to start.";
    }

    function resetButtons() {
        document.getElementById("startBtn").disabled = false;
        document.getElementById("stopBtn").disabled = true;
    }
</script>

</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/translate", methods=["POST"])
def translate():
    data = request.json
    text = data.get("text", "")
    src_code = data.get("srcCode")
    tgt_code = data.get("tgtCode")

    try:
        # Direct GTX endpoint with browser headers (much less likely to be rate-limited than scraper)
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": src_code,
            "tl": tgt_code,
            "dt": "t",
            "q": text
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        resp = requests.get(url, params=params, headers=headers, timeout=8)
        resp.raise_for_status()
        result = resp.json()
        translated = "".join([part[0] for part in result[0] if part[0]])
        return jsonify({"translation": translated})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
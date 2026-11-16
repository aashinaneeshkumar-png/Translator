from flask import Flask, render_template_string, request, jsonify
import requests
from pypdf import PdfReader

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Language Voice & PDF Translator</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: url('/static/unnamed.jpg') no-repeat center center fixed;
            background-size: cover;
            background-color: #f0f2f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px 0;
        }
        .container {
            background: rgba(255, 255, 255, 0.94);
            backdrop-filter: blur(6px);
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.18);
            width: 90%;
            max-width: 680px;
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
        .pdf-section {
            background: #edf2f7;
            border: 1px dashed #a0aec0;
            border-radius: 10px;
            padding: 12px 15px;
            margin-bottom: 15px;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
        }
        .pdf-section input[type="file"] {
            font-size: 14px;
            color: #2d3748;
        }
        #pdfBtn {
            background-color: #38a169;
            padding: 8px 16px;
            border: none;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            cursor: pointer;
            font-size: 14px;
        }
        #pdfBtn:disabled { background-color: #a0aec0; cursor: not-allowed; }
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
            height: 120px;
            padding: 12px;
            border-radius: 10px;
            border: 1px solid #cbd5e0;
            font-size: 15px;
            resize: vertical;
            box-sizing: border-box;
            margin-bottom: 15px;
            background: #f8fafc;
        }
        .btn-group {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
        }
        button.action-btn {
            padding: 11px 18px;
            border: none;
            border-radius: 10px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            color: white;
        }
        button.action-btn:disabled {
            background-color: #a0aec0 !important;
            cursor: not-allowed;
        }
        #startBtn { background-color: #3182ce; }
        #stopBtn { background-color: #e53e3e; }
        #speakOutBtn { background-color: #805ad5; }
        #clearBtn { background-color: #718096; }
    </style>
</head>
<body>

<div class="container">
    <h1>🌍 Voice & PDF Multi-Language Translator</h1>
    
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

    <div class="pdf-section">
        <input type="file" id="pdfInput" accept=".pdf">
        <button id="pdfBtn" onclick="uploadAndTranslatePDF()">📄 Translate PDF</button>
    </div>

    <div class="status" id="status">Speak using the mic OR upload a PDF file above</div>

    <label>📝 Extracted / Spoken Text:</label>
    <textarea id="inputBox" readonly placeholder="Your spoken words or extracted PDF text will appear here..."></textarea>

    <label>💡 Translated Output:</label>
    <textarea id="outputBox" readonly placeholder="Translation will appear here..."></textarea>

    <div class="btn-group">
        <button id="startBtn" class="action-btn" onclick="startListening()">🎤 Start Speaking</button>
        <button id="stopBtn" class="action-btn" onclick="stopListening()" disabled>⏹️ Stop & Translate</button>
        <button id="speakOutBtn" class="action-btn" onclick="readOutputAloud()">🔊 Read Translation</button>
        <button id="clearBtn" class="action-btn" onclick="clearText()">🗑️ Clear</button>
    </div>
</div>

<script>
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition;
    let finalTranscript = "";
    let isRecording = false;
    let latestTranslation = "";

    if (!SpeechRecognition) {
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

    async function uploadAndTranslatePDF() {
        const fileInput = document.getElementById("pdfInput");
        if (!fileInput.files.length) {
            document.getElementById("status").innerText = "⚠️ Please choose a PDF file first.";
            return;
        }

        const tgtSelect = document.getElementById("tgtLang");
        const [tgtSr, tgtCode] = tgtSelect.value.split("|");
        const tgtName = tgtSelect.options[tgtSelect.selectedIndex].text;

        const formData = new FormData();
        formData.append("pdf", fileInput.files[0]);
        formData.append("tgtCode", tgtCode);

        document.getElementById("pdfBtn").disabled = true;
        document.getElementById("status").innerText = "📄 Extracting and translating PDF (this may take a few seconds)...";

        try {
            const response = await fetch("/translate-pdf", {
                method: "POST",
                body: formData
            });
            const data = await response.json();

            if (data.error) throw new Error(data.error);

            appendBox("inputBox", `[PDF: ${fileInput.files[0].name}]:\\n${data.original}`);
            appendBox("outputBox", `[${tgtName}]:\\n${data.translation}`);
            latestTranslation = data.translation;
            document.getElementById("status").innerText = "✅ PDF Translated! Click 'Read Translation' to listen.";
        } catch (err) {
            document.getElementById("status").innerText = "❌ PDF Error: " + err.message;
        } finally {
            document.getElementById("pdfBtn").disabled = false;
        }
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
                const response = await fetch("/translate", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ text, srcCode, tgtCode })
                });
                const data = await response.json();

                if (data.translation) {
                    translatedText = data.translation;
                } else {
                    const mmRes = await fetch(`https://api.mymemory.translated.net/get?q=${encodeURIComponent(text)}&langpair=${srcCode}|${tgtCode}`);
                    const mmData = await mmRes.json();
                    if (mmData.responseData && mmData.responseData.translatedText) {
                        translatedText = mmData.responseData.translatedText;
                    } else {
                        throw new Error("All translation services are currently busy.");
                    }
                }
            }

            latestTranslation = translatedText;
            appendBox("outputBox", `[${tgtName}]: ${translatedText}`);
            document.getElementById("status").innerText = "🔊 Speaking translation...";
            speakOutLoud(translatedText, tgtSr);
        } catch (err) {
            document.getElementById("status").innerText = "❌ Translation Error: " + err.message;
        } finally {
            resetButtons();
        }
    }

    function readOutputAloud() {
        const textToRead = latestTranslation || document.getElementById("outputBox").value;
        if (!textToRead.trim()) {
            document.getElementById("status").innerText = "⚠️ Nothing in the output box to read.";
            return;
        }
        const tgtSr = document.getElementById("tgtLang").value.split("|")[0];
        document.getElementById("status").innerText = "🔊 Reading translation aloud...";
        speakOutLoud(textToRead, tgtSr);
    }

    function speakOutLoud(text, langTag) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = langTag;
        utterance.rate = 0.95;
        utterance.onend = () => {
            document.getElementById("status").innerText = "✅ Done!";
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
        window.speechSynthesis.cancel();
        latestTranslation = "";
        document.getElementById("inputBox").value = "";
        document.getElementById("outputBox").value = "";
        document.getElementById("pdfInput").value = "";
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

def gtx_translate(text, src_code, tgt_code):
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
    resp = requests.get(url, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    result = resp.json()
    return "".join([part[0] for part in result[0] if part[0]])

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
        translated = gtx_translate(text, src_code, tgt_code)
        return jsonify({"translation": translated})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/translate-pdf", methods=["POST"])
def translate_pdf():
    if "pdf" not in request.files:
        return jsonify({"error": "No PDF file uploaded."}), 400

    pdf_file = request.files["pdf"]
    tgt_code = request.form.get("tgtCode", "en")

    try:
        reader = PdfReader(pdf_file)
        pages_text = []
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                pages_text.append(extracted.strip())

        full_text = "\n\n".join(pages_text)
        if not full_text.strip():
            return jsonify({"error": "No selectable text found in this PDF (it may be a scanned image PDF)."}), 400

        # Split into 2,500-character chunks so multi-page PDFs don't hit URL length limits
        chunk_size = 2500
        chunks = [full_text[i:i + chunk_size] for i in range(0, len(full_text), chunk_size)]
        
        # Auto-detect source language ('auto') so any PDF language translates cleanly
        translated_chunks = [gtx_translate(chunk, "auto", tgt_code) for chunk in chunks]
        translated_full = "\n".join(translated_chunks)

        return jsonify({
            "original": full_text,
            "translation": translated_full
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
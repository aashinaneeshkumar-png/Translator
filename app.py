from flask import Flask, render_template_string, request, jsonify, send_file
import io
import re
from pypdf import PdfReader
from gtts import gTTS

app = Flask(__name__)

HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Language Voice & PDF Translator</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: url('/static/unnamed.png') no-repeat center center fixed;
            background-size: cover;
            background-color: #f0f2f5;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 35px 15px 60px 15px;
            gap: 35px;
        }
        .container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(6px);
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.16);
            width: 100%;
            max-width: 680px;
            box-sizing: border-box;
        }
        h1, h2 {
            text-align: center;
            color: #1a202c;
            margin-top: 0;
            font-size: 23px;
        }
        .subtitle {
            text-align: center;
            color: #718096;
            font-size: 13px;
            margin-top: -10px;
            margin-bottom: 18px;
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
        .pdf-upload-bar {
            background: #edf2f7;
            border: 1px dashed #a0aec0;
            border-radius: 10px;
            padding: 14px;
            margin-bottom: 15px;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
        }
        .pdf-lang-row {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
        }
        .pdf-lang-row label {
            margin: 0;
            white-space: nowrap;
        }
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
        #voiceSpeakBtn, #pdfSpeakBtn { background-color: #805ad5; }
        #pdfBtn { background-color: #38a169; }
        .stop-audio-btn { background-color: #dd6b20; }
        .clear-btn { background-color: #718096; }
    </style>
</head>
<body>

<!-- SECTION 1: VOICE TRANSLATOR -->
<div class="container">
    <h1>🎤 Voice-to-Voice Translator</h1>
    <div class="subtitle">Scroll down for PDF Document Upload & Reader ↓</div>
    
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

        <button type="button" class="swap-btn" onclick="swapLanguages()">⇄</button>

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

    <div class="status" id="voiceStatus">Click "Start Speaking", talk, then click "Stop & Translate"</div>

    <label>📝 What you said:</label>
    <textarea id="voiceInputBox" readonly placeholder="Your spoken words will appear here..."></textarea>

    <label>💡 Translated Output:</label>
    <textarea id="voiceOutputBox" readonly placeholder="Translation will appear here..."></textarea>

    <div class="btn-group">
        <button type="button" id="startBtn" class="action-btn" onclick="startListening()">🎤 Start Speaking</button>
        <button type="button" id="stopBtn" class="action-btn" onclick="stopListening()" disabled>⏹️ Stop & Translate</button>
        <button type="button" id="voiceSpeakBtn" class="action-btn" onclick="replayVoice()">🔊 Replay Audio</button>
        <button type="button" class="action-btn stop-audio-btn" onclick="stopAllAudio()">🔇 Stop Audio</button>
        <button type="button" class="action-btn clear-btn" onclick="clearVoice()">🗑️ Clear</button>
    </div>
</div>

<!-- SECTION 2: PDF UPLOAD & READER -->
<div class="container" id="pdf-section">
    <h2>📄 PDF Document Translator & Reader</h2>
    <div class="subtitle">Upload any PDF, translate it, and listen in any language</div>

    <div class="pdf-lang-row">
        <label for="pdfTgtLang">Translate PDF to:</label>
        <select id="pdfTgtLang">
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

    <div class="pdf-upload-bar">
        <input type="file" id="pdfInput" accept=".pdf">
        <button type="button" id="pdfBtn" class="action-btn" onclick="uploadAndTranslatePDF()">📄 Translate PDF</button>
    </div>

    <div class="status" id="pdfStatus">Choose a PDF file above and click "Translate PDF"</div>

    <label>📑 Extracted PDF Text:</label>
    <textarea id="pdfInputBox" readonly placeholder="Extracted PDF content will appear here..."></textarea>

    <label>🌐 Translated PDF Content:</label>
    <textarea id="pdfOutputBox" readonly placeholder="Translated PDF content will appear here..."></textarea>

    <div class="btn-group">
        <button type="button" id="pdfSpeakBtn" class="action-btn" onclick="readPdfAloud()">🔊 Read PDF Aloud</button>
        <button type="button" class="action-btn stop-audio-btn" onclick="stopAllAudio()">🔇 Stop Audio</button>
        <button type="button" class="action-btn clear-btn" onclick="clearPdf()">🗑️ Clear PDF</button>
    </div>
</div>

<script>
    // --- CLIENT-SIDE TRANSLATOR (Runs from User's Browser IP — Never Blocked by Render) ---
    async function browserTranslate(text, srcCode, tgtCode) {
        if (!text.trim() || srcCode === tgtCode) return text;

        // 1. Primary: Google GTX directly from user's browser
        try {
            const gtxUrl = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=" +
                encodeURIComponent(srcCode) + "&tl=" + encodeURIComponent(tgtCode) +
                "&dt=t&q=" + encodeURIComponent(text);
            const res = await fetch(gtxUrl);
            if (res.ok) {
                const data = await res.json();
                return data[0].map(part => part[0] || "").join("");
            }
        } catch (e) {}

        // 2. Fallback: MyMemory API from user's browser
        const pairSrc = (srcCode === "auto") ? "en" : srcCode;
        const mmUrl = "https://api.mymemory.translated.net/get?q=" +
            encodeURIComponent(text.slice(0, 500)) + "&langpair=" + pairSrc + "|" + tgtCode;
        const mmRes = await fetch(mmUrl);
        const mmData = await mmRes.json();
        if (mmData.responseData && mmData.responseData.translatedText) {
            return mmData.responseData.translatedText;
        }
        throw new Error("Translation limit reached. Wait a moment and try again.");
    }

    // --- UNIVERSAL AUDIO PLAYER ---
    let currentAudio = null;

    function stopAllAudio() {
        if (currentAudio) {
            currentAudio.pause();
            currentAudio.currentTime = 0;
            currentAudio = null;
        }
        if (window.speechSynthesis) {
            window.speechSynthesis.cancel();
        }
    }

    async function speakUniversal(text, langCode, bcpTag, statusId) {
        stopAllAudio();
        if (!text || !text.trim()) return;

        try {
            const response = await fetch("/tts", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: text.slice(0, 1500), lang: langCode })
            });
            if (!response.ok) throw new Error("TTS server busy");

            const blob = await response.blob();
            const audioUrl = URL.createObjectURL(blob);
            currentAudio = new Audio(audioUrl);
            currentAudio.onended = () => {
                document.getElementById(statusId).innerText = "✅ Finished reading!";
            };
            await currentAudio.play();
        } catch (err) {
            if (window.speechSynthesis) {
                const utter = new SpeechSynthesisUtterance(text);
                utter.lang = bcpTag;
                utter.onend = () => {
                    document.getElementById(statusId).innerText = "✅ Finished reading!";
                };
                window.speechSynthesis.speak(utter);
            } else {
                document.getElementById(statusId).innerText = "⚠️ Click Replay / Read Aloud button to hear audio.";
            }
        }
    }

    // --- SECTION 1: VOICE TRANSLATOR ---
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition = null;
    let finalTranscript = "";
    let isRecording = false;
    let latestVoiceTranslation = "";

    if (!SpeechRecognition) {
        document.getElementById("voiceStatus").innerText = "❌ Browser doesn't support Speech Recognition. Use Chrome or Edge.";
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
            document.getElementById("voiceStatus").innerText = "🎙️ Hearing: " + (finalTranscript +
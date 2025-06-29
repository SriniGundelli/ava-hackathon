# ava-hackathon
Ava is an AI talent assistant that turns candidate questions into instant answers and auto books 15-min screens, freeing recruiters to focus on human judgement.
# Ava – AI Talent Assistant

> Real‑time voice agent that answers candidate FAQs and auto‑books a 15‑minute recruiter screen – freeing humans to focus on judgement, not logistics.

---

## 🚀 Live demo

| Link                   | What you get                                                                                                                                                 |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Voice agent**        | [https://elevenlabs.io/app/talk-to?agent\_id=agent\_01jy6mpthxf25tywcagfzvqndj](https://elevenlabs.io/app/talk-to?agent_id=agent_01jy6mpthxf25tywcagfzvqndj) |
| **Backend (Bolt.new)** | [https://bolt.new/your-username/Ava-hackathon](https://bolt.new/your-username/Ava-hackathon)                                                                 |
| **Source mirror**      | [https://github.com/srinigundelli/ava-hackathon](https://github.com/srinigundelli/ava-hackathon)                                                             |

---

## 🎯 Features

* Low‑latency voice conversation via **ElevenLabs Conversational AI**.
* RAG‑grounded answers pulled from a live Knowledge Base (culture, perks, openings).
* One‑shot 15‑minute slot booking through **Cal.com** – no forms, no email ping‑pong.
* Twilio SIP trunk so callers can dial a real number.
* Serverless deployment (Vercel) for the custom scheduling tool.
* Nightly Playwright scraper keeps job listings fresh.

---

## 🏗️ Architecture

```
Caller (phone) ──► Twilio ──► ElevenLabs Agent
                         ├──► schedule_call tool ──► Cal.com
                         └──► post‑call webhook ──► ATS / Logs
```

---

## 🛠️ Built with

ElevenLabs Conversational AI; Gemini 2 Flash LLM; Twilio Programmable Voice & SIP; Node.js (TypeScript) + Express; Cal.com v2 REST API; Vercel Serverless Functions; Playwright + Python; GitHub Actions; PostgreSQL on Railway.

---

## 🏃‍♂️ Quick start (local)

```bash
git clone https://github.com/your-username/ava-hackathon.git
cd ava-hackathon
pnpm install   # or npm/yarn
cp .env.example .env   # add your keys
node schedule_call.js  # runs on http://localhost:3000
```

### Required environment variables

| Key              | Where to get it             |
| ---------------- | --------------------------- |
| `CALCOM_API_KEY` | Cal.com ⚙️ → Settings → API |
| `XI_API_KEY`     | ElevenLabs → API keys       |
| `PORT`           | (optional) default 3000     |

---

## 🖥️ Deploy to Vercel

1. Click **Deploy** on Vercel or run `vercel deploy`.
2. Add the same env vars in *Project → Settings → Environment*.
3. Note the live URL (e.g. `https://ava-scheduler.vercel.app`).
4. In ElevenLabs **Agent → Tools**, set the `schedule_call` tool URL to `<your‑URL>/schedule_call`.

---

## 🤖 Agent prompt snippet

```text
If the caller asks to book or when transfer_to_agent is triggered:
  1. Ask for their email if unknown.
  2. Call schedule_call with candidate_name, candidate_email, candidate_phone, time_zone.
  3. Confirm date/time & meeting_url to caller.
  4. Call transfer_to_agent.
```

---

## 🧩 Extending Ava

* **Multi‑language** – toggle Detect Language & upload translated KB.
* **Smart slot selection** – query `/v2/slots` before booking.
* **ATS sync** – push transcript + booking UID into Lever/Greenhouse.
* **Sentiment analysis** – flag high‑intent candidates for priority follow‑up.

---

## 🙌 Acknowledgements

* [ElevenLabs](https://elevenlabs.io) for voice + LLM infra.
* [Cal.com](https://cal.com) for the frictionless scheduling API.
* [Twilio](https://twilio.com) for rock‑solid telephony.

---

## 📝 License

Released under the **Apache 2.0 License** – see `LICENSE` for details.

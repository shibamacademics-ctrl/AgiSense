# AgiSense — Technical One-Pager for Engineering & ML Recruiters

**Project:** AI-Driven Precision Agriculture & Crop Intelligence Platform  
**Live Demo:** [https://agrisense-ruddy-three.vercel.app](https://agrisense-ruddy-three.vercel.app)  
**GitHub Repository:** [https://github.com/shibamacademics-ctrl/AgiSense/tree/copy](https://github.com/shibamacademics-ctrl/AgiSense/tree/copy)  
**Author:** Shibam ([@shibamacademics-ctrl](https://github.com/shibamacademics-ctrl))

---

## 📌 Executive Summary
AgiSense is a production-grade machine learning and full-stack web platform built to solve three critical agricultural challenges: **which crop to plant**, **how to diagnose leaf diseases**, and **what yield volume to expect**. The system combines two scikit-learn tree ensemble models and a fine-tuned MobileNetV2 computer vision CNN into a unified asynchronous FastAPI backend backed by PostgreSQL, containerized with Docker, and served via a modern React SPA.

---

## 🏗️ Technical Architecture & Stack

```
[React 18 + Vite Web App] 
          │ (Async REST / JSON / Multipart Form)
          ▼
   [FastAPI Gateway] ── (JWT Auth / PBKDF2 Hashing)
          │
          ├──> [Crop Recommendation] ── Random Forest Classifier (99.55% Test Accuracy)
          ├──> [Disease Diagnosis]   ── MobileNetV2 Transfer Learning (87.31% Accuracy, 15 Classes)
          ├──> [Yield Prediction]    ── Random Forest Regressor (R² = 0.9786, RMSE = 12,449 hg/ha)
          │
          ▼
   [PostgreSQL 16] ── Query Auditing & Farmer History (JSONB Payloads)
```

- **Frontend:** React 18, Vite, Lucide Icons, Modern responsive CSS.
- **Backend:** Python 3.11, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy 2.0.
- **ML / Data:** Scikit-Learn, TensorFlow CPU 2.17, XGBoost, Pandas, NumPy, Pillow.
- **Cloud & DevOps:** Docker multi-stage builds, Docker Compose, Render Blueprint (`render.yaml`), Railway, Vercel SPA.

---

## 🎯 Quantitative Model Results & Metrics

| Module | Core Architecture | Test Metric #1 | Test Metric #2 | Key Engineering Insight |
| :--- | :--- | :--- | :--- | :--- |
| **Crop Recommendation** | Random Forest (100 trees) | **99.55% Accuracy** | **99.55% Macro F1** | Ensemble tree out-performed XGBoost (99.09%) by avoiding boundary overfitting on small feature spaces (N, P, K, rainfall, pH). |
| **Disease Detection** | MobileNetV2 (ImageNet Pretrained) | **87.31% Accuracy** | **87.36% Macro Recall** | High recall (>90–100%) on critical bacterial spots and potato blights where false negatives are catastrophic to crops. |
| **Yield Forecasting** | Random Forest Regressor | **$R^2 = 0.9786$** | **RMSE = 12,449.9 hg/ha** | Outperformed Linear Regression ($R^2=0.7551$) by capturing non-linear interactions between crop genetics (Item: 62.1% importance) and regional climate (Area: 19.8%). |

---

## 💡 Key Engineering Decisions & Tradeoffs

1. **Why MobileNetV2 over Heavyweight Vision Transformers (ViT) or ResNet-50?**
   - *Constraint:* Edge deployability, inference latency, and memory budgets on cloud free tiers (<512 MB RAM).
   - *Choice:* MobileNetV2’s inverted residual blocks and depthwise separable convolutions offer a 9.8 MB model footprint and ~120 ms CPU inference time, compared to 100MB+ for ResNet-50 with negligible accuracy loss on leaf classification.

2. **Why Asynchronous Non-Blocking Query Auditing?**
   - Query history is persisted to PostgreSQL on a best-effort basis without holding the client HTTP response thread. If the database connection is slow or down, the user still receives their real-time prediction instantly.

3. **Multi-Stage Unified Docker Architecture:**
   - Combines a Node.js 20 build stage with a Python 3.11-slim runner stage.
   - Built assets are served directly through FastAPI static file routing when deployed as a single container, or decoupled cleanly when frontend is on Vercel and backend is on Render/Railway.

---

## 📈 Scalability Considerations (10 users $\rightarrow$ 10,000 users)

- **Model Serving Decoupling:** Move heavy CNN inference to Triton Inference Server or AWS SageMaker endpoints behind an async message queue (Celery + Redis / RabbitMQ).
- **Edge Deployment:** Export MobileNetV2 to quantized TensorFlow Lite (INT8) or ONNX for sub-50ms offline inference in client mobile browsers.
- **Read Replicas & Caching:** Implement Redis caching on static soil/yield queries and read replicas on PostgreSQL for farmer query history.

---

## 🔗 Live Links & Contact
- **Live Frontend:** [https://agrisense-ruddy-three.vercel.app](https://agrisense-ruddy-three.vercel.app)
- **Codebase:** [github.com/shibamacademics-ctrl/AgiSense/tree/copy](https://github.com/shibamacademics-ctrl/AgiSense/tree/copy)
- **Author:** Shibam ([shibamacademics-ctrl](https://github.com/shibamacademics-ctrl))

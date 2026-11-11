# AgiSense: 2-Minute Demo Script & Engineering Tradeoffs Presentation

This document contains a timed 2-minute pitch script, slide outlines for portfolio presentations, and deep-dive technical tradeoff explanations for technical interviews and recruiter screenings.

---

## ⏱️ 2-Minute Technical Demo Script

**Total Duration:** 2 minutes (120 seconds)  
**Presenter Goal:** Show live capabilities, explain architectural choices, and demonstrate engineering maturity.

---

### [0:00 – 0:25] The Hook & Problem Statement
> *"Hello everyone! Today I'm showcasing **AgiSense**, an end-to-end precision agriculture intelligence platform built to tackle three core questions every farmer and agronomist faces: What crop should I plant given my soil chemistry? What disease is damaging my crop leaves? And what yield volume can I realistically expect at harvest?*
> 
> *Instead of leaving machine learning models in isolated Jupyter notebooks, I engineered AgiSense into a fully containerized, production-grade cloud application with a high-performance FastAPI backend, a modern React dashboard, and PostgreSQL persistence."*

---

### [0:25 – 0:50] Feature 1: Soil-Based Crop Recommendation (Live Action)
> *(Action: Navigate to "Crop Recommendation" tab. Enter Nitrogen=90, Phosphorus=42, Potassium=43, Temp=21°C, Humidity=82%, pH=6.5, Rainfall=202mm. Click "Recommend Crop".)*
> 
> *"Let's start with our Crop Recommendation module. I'm providing real soil nutrient levels—NPK—along with local rainfall and climate figures. Within milliseconds, our Random Forest classifier evaluates the feature vector and recommends Rice with 91% confidence, along with ranked viable alternatives like Jute and Maize.*
> 
> *This model achieved **99.55% test accuracy** across 22 crop classes, beating XGBoost and standard decision trees by resisting overfitting on multi-collinear soil chemistry metrics."*

---

### [0:50 – 1:20] Feature 2: Leaf Pathogen Computer Vision Diagnosis (Live Action)
> *(Action: Switch to "Disease Detection" tab. Drag & drop a tomato leaf photo showing early blight lesions. Click "Analyze Leaf".)*
> 
> *"Next is our automated plant pathologist. When a farmer spots leaf discoloration in the field, they upload a photo. I'm uploading this tomato leaf image. Our backend feeds the $224 \times 224$ tensor through a fine-tuned **MobileNetV2 CNN**.*
> 
> *Immediately, it diagnoses 'Tomato Early Blight' with 94.8% precision, flags a visual action plan recommending specific copper fungicides and pruning steps, and alerts the farmer if confidence drops below 60%. MobileNetV2 was chosen specifically for its inverted residual architecture, keeping memory under 10 megabytes for edge compatibility."*

---

### [1:20 – 1:45] Feature 3: Harvest Yield Prediction & Farmer Auditing (Live Action)
> *(Action: Switch to "Yield Prediction" tab. Enter Year=2024, Area=India, Item=Rice, Rainfall=1083mm. Click "Predict Yield".)*
> 
> *"Third, our Yield Forecasting module estimates harvest volume in both hectograms and tonnes per hectare. Our Random Forest regressor achieves an **$R^2$ of 0.9786** and an RMSE of 12,449 hg/ha, accurately modeling the complex non-linear relationship between crop genetics and regional fertilizer usage.*
> 
> *Notice that every query is asynchronously audited into PostgreSQL using JSONB payloads without degrading user inference latency."*

---

### [1:45 – 2:00] Wrap-up & Deployment
> *"The entire system is Dockerized with multi-stage builds, deployed live on Vercel and Render with automated health checks, and ready for edge deployment via TensorFlow Lite. Thank you, and I’d love to dive into the architecture and trade-offs!"*

---

## 🖥️ Presentation Slides (Tradeoffs & Architecture)

### Slide 1: Architecture & Model Selection Tradeoffs

```
========================================================================================
SLIDE 1: MODEL SELECTION & ARCHITECTURAL TRADEOFFS
========================================================================================

1. TABULAR ENSEMBLE vs. DEEP LEARNING (Crop Recommendation & Yield)
   ┌───────────────────────┬─────────────────────────────────┬─────────────────────────┐
   │ Model Evaluated       │ Evaluation Metric               │ Decision Tradeoff       │
   ├───────────────────────┼─────────────────────────────────┼─────────────────────────┤
   │ Linear Regression     │ R² = 0.7551, RMSE = 42,144 hg   │ Fails on non-linearities│
   │ XGBoost Regressor     │ R² = 0.9554, RMSE = 17,996 hg   │ Fast, but higher error  │
   │ Random Forest (Chosen)│ R² = 0.9786, RMSE = 12,449 hg   │ Superior generalization │
   └───────────────────────┴─────────────────────────────────┴─────────────────────────┘
   Tradeoff Note: Tabular deep neural networks (e.g., TabNet) were tested but required
   5x more training epochs with higher inference latency without beating tree ensembles.

2. COMPUTER VISION ARCHITECTURE (Disease Detection)
   ┌───────────────────────┬───────────────────┬───────────────────┬───────────────────┐
   │ Model Architecture    │ Model Size        │ CPU Inference     │ Test Accuracy     │
   ├───────────────────────┼───────────────────┼───────────────────┼───────────────────┤
   │ Vision Transformer    │ 340 MB            │ 850 ms            │ 88.1%             │
   │ ResNet-50             │ 98 MB             │ 320 ms            │ 87.9%             │
   │ MobileNetV2 (Chosen)  │ 9.8 MB            │ 120 ms            │ 87.31%            │
   └───────────────────────┴───────────────────┴───────────────────┴───────────────────┘
   Tradeoff Note: Accepted a negligible 0.6% accuracy delta in exchange for a 10x smaller
   memory footprint and 3x faster CPU execution—essential for low-tier cloud & mobile.
========================================================================================
```

---

### Slide 2: Real-World Data Limitations & Production Scalability

```
========================================================================================
SLIDE 2: DATA CHALLENGES & SCALING FROM 10 TO 10,000 CONCURRENT USERS
========================================================================================

A. DATA LIMITATIONS IN PRODUCTION
   • Laboratory vs. Wild Imagery: PlantVillage images have plain backgrounds. Wild field
     photos suffer from dynamic shadows and background clutter.
     -> Mitigation: Implemented confidence thresholding (<60% warning) and data augmentations.
   • Historical FAO Data Grain: Yield dataset operates at country/macro level rather than
     individual micro-plots.
     -> Next Step: Integrate satellite NDVI (Sentinel-2) and farm-level IoT soil moisture.

B. PRODUCTION SCALABILITY BLUEPRINT (10 -> 10,000 Users)
   
    [10 Concurrent Users]                [10,000 Concurrent Users]
    ---------------------                ------------------------
    Single Uvicorn instance              Horizontal Pod Autoscaling (Kubernetes / ECS)
    Direct synchronous ML inference      Asynchronous Task Queue (Celery + Redis / RabbitMQ)
    In-memory model caching              Dedicated Triton Inference Server with GPU instances
    Direct DB connection pool            PgBouncer connection pooling + Read Replicas
    Cloud server inference only          TensorFlow Lite (INT8) client-side browser inference
========================================================================================
```

---

## 🎯 Interviewer Q&A Prep Cheat-Sheet

**Q: Why did you pick Random Forest over XGBoost for crop recommendation?**  
*A: XGBoost is prone to over-fitting on small tabular feature sets with sharp decision boundaries. In our 5-fold cross validation, Random Forest demonstrated a slightly higher generalizability score (99.43% vs 98.92%) and required zero scaling or complex gradient tuning.*

**Q: What would break first if 1,000 farmers uploaded photos simultaneously?**  
*A: The TensorFlow CPU image preprocessing and matrix multiplication would bottleneck the single Python GIL process and exhaust memory. To fix this, I would decouple image inference behind an S3 presigned upload URL and an async queue (Celery/SQS) feeding a dedicated Triton or TorchServe worker pool.*

**Q: Why use PostgreSQL JSONB for query history instead of a traditional relational schema?**  
*A: Each query type (crop recommendation, disease diagnosis, yield prediction) has fundamentally different payload shapes. PostgreSQL's JSONB gives us the flexibility of a document store like MongoDB while retaining ACID guarantees and relational foreign keys for the user account model.*


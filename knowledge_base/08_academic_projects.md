# Academic Projects (Undergraduate, Research & Graduate)

## Summary
My academic projects gave me a strong foundation in NLP, computer vision, and applied machine learning. The NLP capstone exposed me to speech-to-text and sentiment analysis; the YOLOv3 project taught me object detection; and my CMU summer research strengthened my CNN and image-classification experience. Later, my Rotman MMA projects helped me connect these technical skills with real business use cases.

## NLP Capstone — Call Quality & Sentiment Analysis
My undergraduate capstone, supervised by Professor Jonathan Rose, automated the analysis of customer-service / call-center conversations to assess sentiment and service quality. It was a four-person team, all primarily involved in technical development; I owned the data processing, the NLP analysis pipeline, and part of the model experimentation. The pipeline was:

```
Audio Recording → Speech-to-Text → Text Cleaning → Sentiment Analysis
→ Quality Scoring → Final Report / Demo
```

We first used the Google Speech-to-Text API to transcribe call recordings into text, then cleaned the transcripts—removing noise words, splitting sentences, and identifying speaker turns. For sentiment analysis (before LLMs were widespread), we relied on traditional NLP and early deep-learning methods, experimenting with BERT-based sentiment classification and LSTM-based text classification. The goal wasn't generative AI but identifying whether the customer was satisfied, whether negative emotion appeared, and whether call quality met standards. We delivered model-experiment results, an analysis report, and a working demo. This was my early, hands-on exposure to a full NLP pipeline—speech-to-text, text preprocessing, sentiment classification, and business-oriented quality scoring.

## YOLOv3 — Traffic-Sign Detection
This was my final project for a machine-learning course: detecting traffic signs in road imagery and video. We trained and tested a YOLOv3 model on a public traffic-sign dataset. Unlike a plain classifier that only judges whether a sign is present, YOLOv3 performs object detection—classification plus localization—identifying the sign's class and drawing a bounding box around its position. The workflow was:

```
Dataset Preparation → Image Annotation / Preprocessing → YOLOv3 Training
→ Model Evaluation → Detection Demo
```

The model could recognize and localize traffic signs in street-scene images and video, reaching roughly 95% accuracy in our test scenarios. I was responsible for model training, data preprocessing, results visualization, and the final demo. The project clarified the difference between object detection and image classification, and made me comfortable with CNN-based detection architectures.

## CMU Summer Research — CNN Face-Mask Detection
During the COVID-19 pandemic, I conducted summer research alongside a CMU professor on computer-vision-based mask-wearing detection. The goal was to train a CNN to determine whether a face in an image was wearing a mask correctly. The pipeline:

```
Face Image Dataset → Data Preprocessing → CNN Model Training → Validation
→ Mask / No-Mask Classification
```

We used a convolutional neural network for image classification, with classes of Mask / No Mask (extendable to With Mask / Without Mask / Incorrectly Worn Mask). The model reached roughly 96% accuracy on the validation set. I was responsible for data preprocessing, CNN model training, model evaluation, and the experiment report. The project gave me systematic experience with data augmentation, convolutional and pooling layers, overfitting control, and model-evaluation methods.

# IDP Plus — Founder & Full-Stack Developer


## IDP Plus Project Background

After graduating from grad school in 2024, while waiting for my Canadian permanent residency process, during the gap, I co-founded IDP Plus with partners in China as a startup project. Our team brought together software engineers, project managers, and licensed paralegals to build a trusted solution for Chinese drivers traveling abroad.

We identified a common pain point: since China is not a signatory to the International Driving Permit (IDP) Convention, Chinese driver's license holders cannot obtain an official IDP. However, many countries and car rental companies accept a Chinese driver's license accompanied by a professionally translated, internationally compliant driving document. We built IDP Plus to make this process fast, convenient, and reliable.

As the technical lead, I was responsible for the entire product lifecycle—from system architecture, UI/UX design, full-stack development, testing, deployment, and production operations to continuous feature iteration. Beyond engineering, I also collaborated with printing partners, distributors, logistics providers, and marketing teams to launch and operate the business across Chinese social media platforms such as Xiaohongshu (RED) and Douyin.

Today, IDP Plus remains an active business, serving more than 500 customers and processing approximately 20 orders per month, providing both physical and digital international driving document packages to Chinese travelers worldwide.


## One-Line Overview
IDP Plus (idp-plus.com) is an online platform that helps Chinese drivers obtain internationally recognized driver's-license translations and travel documents for renting and driving cars overseas. My target users are Chinese travelers, business travelers, international students, and overseas Chinese communities. The core problem: because China is not part of the International Driving Permit (IDP) convention, a Chinese license can't be used to apply for an official IDP—but many countries and rental companies accept a Chinese driver's license combined with a certified translation and an international driving document. Customers need a convenient, fast, and trustworthy translation-and-certification service, which is exactly what IDP Plus automates.

## Why I Built It & Current Status
I co-founded IDP Plus with a friend while waiting for my Canadian immigration approval. We saw a large and growing market—huge outbound travel volume from China, rising overseas car-rental demand—served by translation services with a poor experience: cumbersome application processes and long turnaround times. We decided to build a highly automated platform to fix that. The project is still operating roughly a year in, with 500+ paying customers and steady sales of about 20 orders per month. Customer acquisition came mainly from Google Search, Xiaohongshu (RED), overseas Chinese and international-student communities, and word-of-mouth referrals, which began to compound naturally as the customer base grew.

## Technical Architecture
**Frontend:** React + TypeScript, handling user-information entry, file upload, order management, and the payment flow. **Backend:** FastAPI, handling OCR processing, data validation, PDF generation, payment callbacks, and email sending. **Cloud:** deployed on Alibaba Cloud with Docker containerization, supporting continuous updates and maintenance. **Third-party services:** Baidu OCR for document recognition, Stripe for payments, and SMTP for automated email delivery.

## Core End-to-End Automation Workflow
The system is essentially fully automated end to end:

```
User Upload → OCR Verification → Information Validation → Stripe Payment
→ PDF Generation → QR Code Generation → Email Delivery → Admin Fulfillment
```

## OCR Verification
Users upload a photo of their driver's license plus their personal information. The system calls Baidu OCR to extract fields—name, license number, date of birth, expiry date—then automatically cross-checks the extracted values against what the user entered (name match, license-number match, date-of-birth match, expiry match). If validation fails, the user can't proceed to payment, which prevents bad orders and removes most manual review.

## Automated PDF Generation
PDF generation is one of the core features. Most pages of the international driving document are fixed; only the personal-information page is generated dynamically. The system automatically fills in the user's personal details, inserts their photo and license information, and inserts the translated content, then produces a standardized PDF. For multilingual support, the user selects a target language (e.g., English, French, Spanish) and the system swaps content using language-specific templates, with free-text portions generated via a translation service. Each document also gets a unique QR code tied to its Order ID and verification record; scanning it shows the original certification record, improving anti-counterfeiting.

## Payment System
Payments use Stripe Checkout, supporting Visa, Mastercard, Apple Pay, and Google Pay. The flow is: create order → Stripe Checkout → payment success → webhook callback → generate PDF → email delivery. Order status (Pending → Paid → Generated → Delivered) updates automatically throughout.

## Admin Backend
I built an admin system so operators can view orders, manually review, skip payment when needed, regenerate a PDF, and check fulfillment/logistics status—making day-to-day operations manageable.

## 95% Reduction in Manual Preparation
The original process was almost entirely manual: receive order → manual review → manual data entry → manual layout → manual PDF generation → manual sending. Now it's: user submits → system validates → auto-generates → auto-sends, with only final printing and shipping requiring human involvement. That reduced manual document-preparation effort by approximately 95%.

## External Partnerships / Operations
The project was more than software—it involved supply-chain coordination. I worked with a printing factory (producing the physical international driving booklets), a logistics provider (SF Express for shipping), and marketing partners for promotion and acquisition—coordinating printing standards, shipping processes, inventory management, and customer delivery.

## My Contribution
I was responsible for the entire technical stack: frontend development, FastAPI backend development, OCR integration, PDF generation, Stripe payment integration, email-delivery automation, cloud deployment, website maintenance, and ongoing feature development.

## Biggest Technical Challenge
The biggest challenge was building a reliable end-to-end automation workflow. Multiple services—OCR, payment processing, PDF generation, email delivery, and administrative workflows—all had to work together correctly. Ensuring that a failure in one stage didn't break the entire pipeline required careful error handling and monitoring.

## Biggest Lesson — Founder Mindset
The biggest lesson I learned was that building a product is very different from building software. Technical implementation is only one part of the challenge—I also had to think about customer acquisition, user experience, operations, logistics, payment systems, and long-term maintenance. It gave me a much stronger product and ownership mindset than working purely as an engineer.

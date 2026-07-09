# IDP Plus — SaaS Document Automation Platform (Startup)

## Overview

IDP Plus is an online platform for Chinese driving-license holders that generates and fulfills multilingual driving-license translation booklets. It supports license upload, OCR-based validation, online payment, automatic multilingual PDF generation, QR-code verification, and admin-side order processing with offline printing and shipping.

Accurate product description: an International Driving Permit-style multilingual driving license translation booklet, i.e. a multilingual driving license translation and verification service (not an official international driving permit).

## Project Background

China is not party to certain international driving-permit conventions, so Chinese license holders renting cars or driving short-term abroad frequently need a translated, certified, or supporting document for their license.

Given the volume of outbound Chinese travelers with this need, the platform was built in cooperation with paralegals, domestic agents, a printing house, and marketing partners. The end-to-end user flow: upload license → fill in information → OCR validation → payment → automatic translation PDF generation → admin printing and binding → shipping.

## Pain Points

1. The traditional process required users to separately arrange translation, layout, and printing.
2. License information was frequently entered incorrectly.
3. Manual order processing was slow.
4. Translation documents lacked a verification mechanism and could be tampered with.
5. Orders, payments, PDFs, and shipping were tracked in separate places.
6. Early-stage budget constraints ruled out building a complex backend system from day one.

## Solution

A lightweight SaaS platform covering the full order lifecycle.

User-facing capabilities: product selection, information entry, license image upload, OCR validation of entered data, shipping address entry, Stripe payment, and PDF download.

Backend capabilities: Baidu OCR field extraction, comparison of user input against OCR fields, UUID-based order isolation, automatic PDF generation, QR-code verification link generation, admin email notification, user email notification, and admin operations for re-issuing orders, resending files, and generating documents with validation bypassed.

## Architecture

Order pipeline (left to right):

```
User → Streamlit Frontend → FastAPI Backend → Baidu OCR → Field Validation
     → PDF Generator → Stripe Checkout → Webhook (payment success)
     → Order Confirmation → Admin Email + User Email
     → Print / Booklet Assembly / Shipping
```

## Core Technical Design 1 — OCR Validation

After a user uploads a license image, the backend calls Baidu OCR to extract license fields as key-value pairs: name, date of birth, license number, expiry date, and others. The system then compares the OCR output against the information the user typed in.

Deliberate responsibility boundary: OCR does not auto-fill the form; users enter their own information and the system only validates it. If OCR auto-fills wrong information, responsibility may fall on the platform; if the user enters the information and the system only validates, the user remains responsible for the submitted data. This is a product-liability boundary design.

## Core Technical Design 2 — UUID Order Isolation

Every order receives a UUID, and all related artifacts are keyed by it: order_id = UUID, pdf_file = UUID.pdf, and the Stripe session id maps back to the UUID. This prevents PDF mix-ups under concurrent orders — one user's generated PDF can never be downloaded by another user.

## Core Technical Design 3 — Stripe Payment + Webhook

Payment uses Stripe Checkout. After the user pays, a Stripe webhook delivers the payment_success event to the backend. Only on this event does the backend update the order status, unlock the PDF download, send the user confirmation email, send the admin order email, and trigger printing and shipping. Invariant: no payment, no final PDF delivery.

## Core Technical Design 4 — PDF Generation

The system generates a multilingual PDF translation page from user information and target languages, using a dynamic PDF generation pipeline in which user-specific fields are injected into a predefined backend template. The PDF serves as the user's electronic download, the admin's print master for booklet binding, and the order archive record.

## Core Technical Design 5 — QR Code Verification

Each translation booklet embeds a QR code that resolves to a verification page displaying the originally submitted information, preventing after-the-fact tampering with the printed pages.

Verification flow: User Information → Encrypted Payload → QR Code URL → Verification Service → Decryption → Original Information Display.

Properties: the URL cannot be arbitrarily modified, user information is encrypted in the payload, scanning shows the information as recorded at generation time, and the mechanism raises the document's trustworthiness and tamper resistance.

## Core Technical Design 6 — Admin Portal

Admin functionality was added iteratively in response to real operational needs. Admins can view orders, re-issue PDFs, generate documents with OCR validation bypassed, handle customer-service cases, and regenerate lost or replacement orders. The portal reflects continuous iteration driven by live business requirements rather than a one-off demo.

## Technology Stack

Frontend: Streamlit. Backend: Python + FastAPI. OCR: Baidu OCR API. Payment: Stripe Checkout + webhooks. PDF: Python template-based PDF generation. Verification: encrypted QR-code URLs. Deployment: Docker. Notifications: automated admin and user email.

## Business Results

The platform has processed nearly 500 paid orders to date, with current monthly sales of around 50 booklets — real users, real payments, real fulfillment.

## Technology Trade-off — Streamlit Frontend

Streamlit was chosen at the MVP stage to minimize frontend development cost and concentrate effort on OCR, payment, PDF generation, and the order workflow; this enabled a fast launch. As requirements grew, Streamlit's limits surfaced: complex page-state management, limited UI customization, difficult multi-page flow maintenance, less flexible interaction than React/TypeScript, and rising refactoring cost. Conclusion: Streamlit was the right choice for an early-stage MVP, and a customer-facing production SaaS frontend would migrate to React or Next.js.

## Technology Trade-off — No Dedicated Database at MVP Stage

At the MVP stage the platform intentionally avoided maintaining a full user database to reduce operational cost, privacy risk, and maintenance complexity. Instead: Stripe records payments, email records orders, PDFs serve as delivery records, and the admin mailbox acts as a lightweight order archive. The planned upgrade path is PostgreSQL with order, user, payment, shipment, and PDF-metadata tables.

## Key Capabilities Demonstrated

Zero-to-one product delivery, real user-demand analysis, SaaS platform development, OCR integration, payment integration, automated PDF generation, order-fulfillment workflow design, security and verification design, Docker deployment, and business operations with marketing execution.

## Summary Bullets

- Co-founded IDP Plus, a SaaS-style document automation platform for multilingual driving license translation booklets, processing nearly 500 paid orders with ~50 monthly sales.
- Built an end-to-end order workflow using Streamlit, FastAPI, Baidu OCR, Stripe Checkout, PDF generation, QR-code verification, email automation, and Docker deployment.
- Designed an OCR-based validation pipeline comparing user-submitted information against extracted license fields, reducing manual review effort and preventing data-entry errors.
- Implemented UUID-based order isolation and Stripe webhook handling to securely associate payments, generated PDFs, customer sessions, and admin notifications.
- Developed an encrypted QR-code verification service displaying original submitted information to reduce the risk of document tampering.

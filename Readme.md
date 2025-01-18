# Financial Data Analysis Tool

This repository contains the implementation of various financial data analysis tools developed for a semester project. The project includes multiple assignments and a final integrated system for stock analysis and pricing strategies.

## Table of Contents
1. [Pair Trading Strategy with Highcharts](#pair-trading-strategy-with-highcharts)
2. [Backtesting with Backtrader](#backtesting-with-backtrader)
3. [Django Rest Framework API](#django-rest-framework-api)
4. [Secured Function and Data API](#secured-function-and-data-api)
5. [Tracker Functionality](#tracker-functionality)
6. [Docker Deployment](#docker-deployment)
7. [Stock Selection Module](#stock-selection-module)
8. [Stock Selection Website](#stock-selection-website)
9. [Stock Pricing Strategies](#stock-pricing-strategies)
10. [PER River Chart](#per-river-chart)
11. [Resistance and Support Lines](#resistance-and-support-lines)
12. [Technical Indicators](#technical-indicators)
13. [Final Project: Signal Detection and K-Line Patterns](#final-project-signal-detection-and-k-line-patterns)

---

## Pair Trading Strategy with Highcharts

**Objective:**
- Implement a pair trading strategy using the Distance Method.
- Visualize results using Highcharts and DataTables.
- Integrate with Yahoo Finance API for real-time data fetching.

**Usage:**
1. Input stock tickers, start date, end date, and parameters on the web interface.
2. The backend processes the request and calculates results.
3. The frontend renders charts and displays calculated results.

---

## Backtesting with Backtrader

**Objective:**
- Build and backtest simple entry and exit strategies.
- Use Backtrader to visualize and evaluate strategy performance.

**Usage:**
1. Input stock code, RSI parameters, and strategy settings.
2. The backend processes and returns the results.
3. View interactive charts and performance tables on the frontend.

---

## Django Rest Framework API

**Objective:**
- Create RESTful APIs using Django Rest Framework for data exchange between frontend and backend.

**Usage:**
- Test APIs using Postman with endpoints for backtesting and tracking.

---

## Secured Function and Data API

**Objective:**
- Enhance API security with token authentication and secure data handling.

**Usage:**
1. Obtain access tokens through the login endpoint.
2. Use the token to access secured APIs for data retrieval and processing.

---

## Tracker Functionality

**Objective:**
- Enable users to track stocks or strategies and receive automated daily reports via email.

**Usage:**
1. Add a stock to the tracker via the web interface.
2. View daily tracking results and reports.

---

## Docker Deployment

**Objective:**
- Containerize the project with Docker for modular deployment.

**Usage:**
1. Build Docker images for each module (Auth, API, Web).
2. Use Docker Compose to manage and run the containers.

---

## Stock Selection Module

**Objective:**
- Implement stock selection strategies using Finlab and visualize the results.

**Usage:**
- Use Jupyter Notebook to test the Finlab module with customized stock selection conditions.

---

## Stock Selection Website

**Objective:**
- Build a Django-based website for stock selection using the Finlab module.

**Usage:**
1. Input stock selection criteria on the website.
2. View filtered results and technical charts.

---

## Stock Pricing Strategies

**Objective:**
- Implement four stock pricing methods (DDM, PBR, PER, High-Low Price).

**Usage:**
1. Input stock code and historical data range on the website.
2. View price ranges and real-time comparisons.

---

## PER River Chart

**Objective:**
- Visualize stock pricing with PER multipliers.

**Usage:**
- Generate PER river charts with user-defined parameters on the website.

---

## Resistance and Support Lines

**Objective:**
- Calculate and visualize resistance and support lines using various methods.

**Usage:**
- Input stock code and parameters to view calculated lines and breakout points.

---

## Technical Indicators

**Objective:**
- Implement and visualize technical indicators like KD, MACD, Bollinger Bands, RSI, ADX, and DMI.

**Usage:**
- Input parameters for each indicator and view interactive charts on the website.

---

## Final Project: Signal Detection and K-Line Patterns

**Objective:**
- Integrate various strategies and technical indicators into a comprehensive signal detection system.
- Add K-line pattern detection and tracking functionality.

**Usage:**
1. Input stock code and parameters on the frontend.
2. View integrated analysis results, including pricing strategies and signal detections.

---

## Getting Started
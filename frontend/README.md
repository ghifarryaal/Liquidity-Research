# LiquidityResearch Frontend

This is the dashboard interface for **LiquidityResearch**, built with Next.js and optimized for high-density financial data visualization.

## 📊 Features
- **Real-time Market Overview:** Live tracking of index momentum and panic levels.
- **Dynamic Cluster View:** Visual grouping of stocks based on behavioral patterns.
- **Stock Deep-Dive:** Detailed analysis including trade plans and machine learning confidence scores.
- **Global Macro Panel:** Integrated tracking of DXY and US10Y yields.

## 🚀 Getting Started

1.  **Install dependencies:**
    ```bash
    npm install
    ```

2.  **Run the development server:**
    ```bash
    npm run dev
    ```

3.  **Configuration:**
    The dashboard expects the backend to be running at `http://localhost:8000`. You can configure the API URL in `.env.local`:
    ```text
    NEXT_PUBLIC_API_URL=http://localhost:8000
    ```

## 🏗 Architecture
- **Next.js (App Router):** Modern React framework for high-performance rendering.
- **Framer Motion:** Smooth micro-animations for an interactive UI.
- **SWR:** Efficient data fetching and revalidation strategy.
- **Material Symbols:** Professional-grade iconography.

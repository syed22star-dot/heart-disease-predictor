# Production Deployment & SEO Discovery Guide

This guide details the step-by-step process to host your CardioInsight AI app permanently online and optimize it so that when users search Google for "heart disease risk calculator" or "heart disease predictor," they can easily find and use your platform.

---

## Part 1: Production Hosting Options

Since the application uses a **Flask backend** (to compute analytics, serve the site, and act as a model fallback) and a **Tailwind frontend**, you need a hosting service that runs Python/WSGI applications.

### Option A: Render.com (Recommended - Easiest & Free Tier)
Render is the simplest modern cloud platform for hosting Flask applications directly from GitHub.

1. **Upload Code to GitHub:**
   - Create a new repository on GitHub (e.g., `heart-disease-predictor`).
   - Push the contents of your `Heart` folder to this repository. Ensure `app.py`, `requirements.txt`, `heart.csv`, and all `.pkl` model files are in the root of the repository.
2. **Create a Render Web Service:**
   - Sign up for a free account at [Render.com](https://render.com).
   - Click **New +** and select **Web Service**.
   - Connect your GitHub account and select your repository.
3. **Configure Settings:**
   - **Name:** `cardioinsight-ai` (or your preferred name)
   - **Region:** Choose the one closest to your target audience.
   - **Branch:** `main`
   - **Runtime:** `Python`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app` *(Render automatically handles Gunicorn WSGI running)*
4. **Deploy:**
   - Click **Create Web Service**. Render will build and deploy your app. You will get a free HTTPS URL like `https://cardioinsight-ai.onrender.com`.

### Option B: Google Cloud Run (Best for Scalability & "Deploy in Google")
If you want to host it directly inside Google Cloud Platform (GCP) with high reliability and zero-cost scaling when idle.

1. **Add a `Dockerfile` to the Heart Directory:**
   ```dockerfile
   FROM python:3.12-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   EXPOSE 8080
   CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
   ```
2. **Deploy via Google Cloud SDK:**
   - Install the Google Cloud SDK and run:
     ```bash
     gcloud auth login
     gcloud config set project [YOUR_PROJECT_ID]
     gcloud run deploy heart-disease-predictor --source . --region us-central1 --allow-unauthenticated
     ```
   - Cloud Run will package your application, upload it to Google Artifact Registry, and host it as a serverless container with a public URL.

---

## Part 2: Custom Domain Registration

To look professional and rank well on search engines, purchase a custom domain rather than using a free `.onrender.com` or `.run.app` subdomain.

1. **Pick a Keyword-Rich Domain:**
   - Search engines prioritize domains containing the primary keywords. Try to register names like:
     * `heartdiseasepredictor.com`
     * `cardioinsightai.org`
     * `heartriskcalculator.net`
   - Use registrars like **Google Domains (Squarespace)**, **Namecheap**, or **GoDaddy**.
2. **Link the Domain:**
   - In Render or Google Cloud Run settings, add your custom domain.
   - Configure your domain registrar's DNS settings by adding the recommended **CNAME** or **A records** pointing to your host.

---

## Part 3: Search Engine Optimization (SEO) for "Heart Disease"

To rank on Google's search results page (SERP) when normal users search for "heart disease", you need to configure SEO elements.

### 1. Register with Google Search Console
Google Search Console is the direct way to tell Google your website exists and request indexing.
- Go to [Google Search Console](https://search.google.com/search-console).
- Add your custom domain.
- Verify ownership using a DNS TXT record.
- Use the **URL Inspection Tool** to paste your website link and click **Request Indexing**. This forces Google’s crawler (Googlebot) to index your page within hours instead of waiting weeks.

### 2. Generate a `sitemap.xml` & `robots.txt`
Place these two files in the templates/static directory of your Flask app so Googlebot can read them.

#### `robots.txt`
```text
User-agent: *
Allow: /
Sitemap: https://yourdomain.com/sitemap.xml
```

#### `sitemap.xml`
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://yourdomain.com/</loc>
    <lastmod>2026-06-25</lastmod>
    <changefreq>monthly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
```

### 3. Open Graph (OG) Tags for Social Media Share
When users share your site on LinkedIn, Twitter, or Facebook, these tags render a rich preview. Add them inside the `<head>` of `index.html`:
```html
<!-- Open Graph / Facebook -->
<meta property="og:type" content="website">
<meta property="og:url" content="https://yourdomain.com/">
<meta property="og:title" content="CardioInsight AI - Heart Disease Risk Predictor">
<meta property="og:description" content="Calculate cardiovascular health risk instantly with CardioInsight AI. Formulated by Syed Tahir Ahamed R using UCI machine learning models.">
<meta property="og:image" content="https://yourdomain.com/static/og-preview.jpg">

<!-- Twitter -->
<meta property="twitter:card" content="summary_large_image">
<meta property="twitter:url" content="https://yourdomain.com/">
<meta property="twitter:title" content="CardioInsight AI - Heart Disease Risk Predictor">
<meta property="twitter:description" content="Calculate cardiovascular health risk instantly with CardioInsight AI. Formulated by Syed Tahir Ahamed R using UCI machine learning models.">
<meta property="twitter:image" content="https://yourdomain.com/static/og-preview.jpg">
```

### 4. Schema.org JSON-LD Structured Data
Adding structured metadata tells search engines exactly what your page is (a web application built for medical health calculations), allowing Google to show Rich Snippets. Add this inside the `<head>` of `index.html`:
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "CardioInsight AI",
  "applicationCategory": "HealthApplication",
  "operatingSystem": "All",
  "author": {
    "@type": "Person",
    "name": "Syed Tahir Ahamed R"
  },
  "description": "An interactive, zero-latency clinical cardiovascular risk calculator trained on historical patient records.",
  "offers": {
    "@type": "Offer",
    "price": "0.00",
    "priceCurrency": "USD"
  }
}
</script>
```

### 5. Content, Performance, and Backlinks
- **Fast Load Speed (Core Web Vitals):** Google ranks fast sites higher. Since CardioInsight AI runs predictions locally on the browser in **0ms** (without waiting for backend queries), it will score extremely high on Google PageSpeed Insights, giving you a competitive edge.
- **Link Building (Backlinks):** Google ranks websites based on how many other sites link to them. Link your website in your GitHub repositories, your LinkedIn bio, write a medium post about it, share it in student ML forums, and submit it to online directories.

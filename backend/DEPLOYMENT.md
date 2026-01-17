# Deployment Guide

This guide details how to deploy the **AI Resume Screener** to **Railway** or **Render**.

## Prerequisites
- GitHub Repository with this code.
- Accounts on Railway or Render.

---

## A. Railway Deployment (Recommended)

1.  **Create Project**
    - Go to [Railway Dashboard](https://railway.app/).
    - Click **New Project** > **Deploy from GitHub repo**.
    - Select your repository.

2.  **Add Services**
    - Click **New** > **Database** > **Add PostgreSQL**.
    - Click **New** > **Database** > **Add Redis**.

3.  **Configure Environment Variables**
    - Go to the **Variables** tab of your Django App service.
    - Add the following:
      - `DJANGO_SETTINGS_MODULE`: `core.settings.prod`
      - `SECRET_KEY`: (Generate a strong random string)
      - `ALLOWED_HOSTS`: `*` (or your railway app domain)
      - `CSRF_TRUSTED_ORIGINS`: `https://your-app-name.up.railway.app`
      - `DATABASE_URL`: `${{PostgreSQL.DATABASE_URL}}` (Select from dropdown)
      - `CELERY_BROKER_URL`: `${{Redis.REDIS_URL}}` (Select from dropdown)
      - `CELERY_RESULT_BACKEND`: `${{Redis.REDIS_URL}}` (Select from dropdown)
      - `PORT`: `8000`

4.  **Configure Start Command**
    - Go to **Settings** > **Deploy** > **Start Command**.
    - Set it to:
      ```bash
      python manage.py migrate && gunicorn core.wsgi:application --config gunicorn.conf.py
      ```
    - This ensures migrations run automatically on every deploy.

5.  **Deploy**
    - Railway usually triggers a deploy automatically. Monitor the **Deployments** logs.

6.  **Verify**
    - Opening the public URL should show the Not Found page (since `/` isn't defined) or API response.
    - Go to `/api/docs/` to see Swagger UI.

---

## B. Render Deployment

1.  **Create Web Service (Django)**
    - Go to [Render Dashboard](https://dashboard.render.com/).
    - Click **New** > **Web Service**.
    - Connect your repo.
    - **Runtime**: Python 3.
    - **Build Command**:
      ```bash
      pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
      ```
    - **Start Command**:
      ```bash
      gunicorn core.wsgi:application --config gunicorn.conf.py
      ```

2.  **Environment Variables (Web Service)**
    - `DJANGO_SETTINGS_MODULE`: `core.settings.prod`
    - `SECRET_KEY`: (Random string)
    - `DATABASE_URL`: (Internal Connection String from Render Postgres - see step 3)
    - `CELERY_BROKER_URL`: (Internal Connection String from Render Redis - see step 3)
    - `CELERY_RESULT_BACKEND`: (Same as above)
    - `PYTHON_VERSION`: `3.11.0` (Optional)

3.  **Add Components**
    - **PostgreSQL**: Create a new Postgres DB on Render. Copy the **Internal Connection URL** to `DATABASE_URL` above.
    - **Redis**: Create a new Redis on Render. Copy the **Internal Connection URL** to `CELERY_BROKER_URL` above.

4.  **Create Background Worker (Celery)**
    - Click **New** > **Background Worker**.
    - Connect same repo.
    - **Build Command**: `pip install -r requirements.txt`
    - **Start Command**: `celery -A core worker -l info`
    - **Environment Variables**: Add the exact same variables as the Web Service (DB, Redis, settings, etc).

---

## C. Important Limitations & storage

### Ephemeral Filesystem
Both Railway and Render use **ephemeral storage**. This means any file uploaded to `media/` (i.e., Resumes) will be **deleted** whenever the app restarts or redeploys.

### Solution: Amazon S3 / Cloudinary
For production use, you **MUST** configure a persistent storage backend.

**Steps to Enable S3:**

1.  **Install dependencies**:
    ```bash
    pip install django-storages[boto3]
    ```

2.  **Update `core/settings/prod.py`**:
    ```python
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        }
    }
    ```

3.  **Add Environment Variables**:
    - `AWS_ACCESS_KEY_ID`
    - `AWS_SECRET_ACCESS_KEY`
    - `AWS_STORAGE_BUCKET_NAME`
    - `AWS_S3_REGION_NAME`

---

## D. Local Verification Commands

To verify the production setup locally (simulating the environment):

1.  **Install Production Deps**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Set Environment Variables** (PowerShell example):
    ```powershell
    $env:DJANGO_SETTINGS_MODULE="core.settings.prod"
    $env:SECRET_KEY="test_secret"
    $env:ALLOWED_HOSTS="*"
    $env:DATABASE_URL="postgres://ai_user:ai_pass@localhost:5433/ai_resume" # Ensure DB is running
    $env:CELERY_BROKER_URL="redis://127.0.0.1:6379/0"
    ```

3.  **Run Migrations**:
    ```bash
    python manage.py migrate
    ```

4.  **Collect Static**:
    ```bash
    python manage.py collectstatic --noinput
    ```

5.  **Run Server**:
    ```bash
    gunicorn core.wsgi:application --config gunicorn.conf.py
    ```

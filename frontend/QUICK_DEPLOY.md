# ⚡ Vercel Quick Deploy

## 🚀 3 алхам

### 1. Vercel дээр project үүсгэх

**⚠️ ЧУХАЛ: Repo дээр `frontend` болон `backend` хоёр folder байгаа тул Root Directory заавал тохируулах!**

**Browser дээр:**
1. [vercel.com/new](https://vercel.com/new) руу оч
2. GitHub repo-оо сонгох: `Dorjnyam/MSQ`
3. **Root Directory**: `frontend` гэж бичих (эсвэл `./frontend`)
   - ⚠️ Энэ нь заавал шаардлагатай! Vercel-д зөвхөн `frontend` folder-ийг deploy хийхийг заах
4. Framework: Next.js (автоматаар илрүүлнэ)
5. Deploy хийх

### 2. Environment Variable нэмэх

**Vercel Dashboard:**
1. Project → Settings → Environment Variables
2. Add New:
   - **Name**: `NEXT_PUBLIC_BACKEND_URL`
   - **Value**: `https://test-generator-backend.fly.dev` (Backend deploy хийсний дараа)
   - **Environment**: Production, Preview, Development (бүгдийг сонгох)

### 3. Redeploy

Vercel Dashboard → Deployments → Latest → Redeploy

## ✅ Бэлэн!

Frontend URL: `https://your-project.vercel.app`

## 📝 Дараагийн алхам

Backend-ийг Fly.io дээр deploy хийх:
```bash
cd backend
fly secrets set FRONTEND_URL=https://your-project.vercel.app
fly deploy
```


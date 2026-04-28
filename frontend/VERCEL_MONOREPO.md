# Vercel Monorepo Setup (Frontend + Backend)

## 📁 Таны Repo бүтэц

```
Dorjnyam/MSQ/
├── frontend/     ← Vercel дээр энэ folder-ийг deploy хийх
├── backend/     ← Fly.io дээр энэ folder-ийг deploy хийх
└── ...
```

## ⚠️ Чухал: Root Directory тохируулах

Vercel дээр project үүсгэхдээ **Root Directory** заавал тохируулах хэрэгтэй!

### Vercel Dashboard дээр:

1. **Import Project** → GitHub repo сонгох: `Dorjnyam/MSQ`
2. **Configure Project** хэсэг дээр:
   - **Root Directory**: `frontend` гэж бичих
   - Эсвэл: `./frontend`
3. **Framework Preset**: Next.js (автоматаар илрүүлнэ)
4. Deploy хийх

### Screenshot хэсэг:

```
┌─────────────────────────────────────┐
│ Configure Project                    │
├─────────────────────────────────────┤
│ Framework Preset: [Next.js ▼]      │
│ Root Directory: [frontend      ]    │ ← ЭНЭ ХЭСЭГТ frontend бичих!
│ Build Command: [npm run build]      │
│ Output Directory: [.next]            │
└─────────────────────────────────────┘
```

## ✅ Deploy хийх алхам

### 1. Vercel дээр project үүсгэх

1. [vercel.com/new](https://vercel.com/new)
2. `Dorjnyam/MSQ` repo сонгох
3. **Root Directory**: `frontend` бичих
4. Deploy

### 2. Environment Variable тохируулах

Backend deploy хийсний дараа:

```
NEXT_PUBLIC_BACKEND_URL=https://test-generator-backend.fly.dev
```

### 3. Redeploy

Environment variable нэмсний дараа redeploy хийх.

## 🔍 Хэрэв Root Directory тохируулаагүй бол

Vercel бүх repo-г deploy хийх гэж оролдох бөгөөд:
- ❌ Build алдаа гарна
- ❌ `package.json` олдохгүй
- ❌ Next.js илрүүлэхгүй

**Шийдэл:**
1. Project Settings → General
2. Root Directory: `frontend` тохируулах
3. Redeploy

## 📝 Checklist

- [ ] Vercel дээр `Dorjnyam/MSQ` repo import хийсэн
- [ ] **Root Directory: `frontend` тохируулсан** ⚠️
- [ ] Deploy хийсэн
- [ ] Frontend URL тэмдэглэсэн: `_________________`
- [ ] Backend deploy хийсэн (Fly.io)
- [ ] `NEXT_PUBLIC_BACKEND_URL` тохируулсан
- [ ] Redeploy хийсэн
- [ ] Test хийсэн ✅

## 🎯 Дараагийн алхам

Backend-ийг Fly.io дээр deploy хийх:
```bash
cd backend
fly secrets set FRONTEND_URL=https://your-frontend.vercel.app
fly deploy
```


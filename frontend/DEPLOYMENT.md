# Vercel Deployment Guide (Frontend)

## ✅ Deploy хийх алхам

### 1. Vercel Account үүсгэх

1. [vercel.com](https://vercel.com) руу оч
2. GitHub account-аар нэвтрэх (эсвэл email)

### 2. Vercel CLI суулгах (Сонголттой)

```bash
npm i -g vercel
```

Эсвэл browser дээрээс шууд deploy хийх боломжтой.

### 3. Frontend folder руу шилжих

```bash
cd frontend
```

### 4. Vercel дээр project үүсгэх

**⚠️ ЧУХАЛ: Таны repo дээр `frontend` болон `backend` хоёр folder байгаа тул Root Directory заавал тохируулах хэрэгтэй!**

**Option A: Browser дээр (Хялбар)**
1. [vercel.com/new](https://vercel.com/new) руу оч
2. GitHub repo-оо сонгох: `Dorjnyam/MSQ`
3. **Root Directory** гэж `frontend` бичих (эсвэл `./frontend`)
   - ⚠️ Энэ нь заавал шаардлагатай! Vercel-д `frontend` folder-ийг deploy хийхийг заах
4. Framework: Next.js (автоматаар илрүүлнэ)
5. Deploy хийх

**Option B: CLI ашиглах**
```bash
vercel
```

### 5. Environment Variables тохируулах

Vercel dashboard дээр:
1. Project → Settings → Environment Variables
2. Дараах variable нэмэх:

```
NEXT_PUBLIC_BACKEND_URL=https://test-generator-backend.fly.dev
```

**Эсвэл CLI ашиглах:**
```bash
vercel env add NEXT_PUBLIC_BACKEND_URL
# Value: https://test-generator-backend.fly.dev
```

### 6. Redeploy хийх

Environment variable нэмсний дараа:
- Vercel dashboard дээр: Deployments → Redeploy
- Эсвэл: `vercel --prod`

## 🔄 Deploy хийх дараалал

### Алхам 1: Frontend deploy (Vercel)
1. ✅ Frontend-ийг Vercel дээр deploy хийх
2. ✅ Frontend URL-ийг тэмдэглэх (жишээ: `https://test-generator.vercel.app`)

### Алхам 2: Backend deploy (Fly.io)
1. ✅ Backend-ийг Fly.io дээр deploy хийх
2. ✅ Frontend URL-ийг CORS дээр тохируулах:
   ```bash
   fly secrets set FRONTEND_URL=https://test-generator.vercel.app
   ```

### Алхам 3: Frontend-ийг дахин deploy хийх
1. ✅ Backend URL-ийг frontend environment variable дээр тохируулах
2. ✅ Redeploy хийх

## 📝 Environment Variables

### Vercel дээр тохируулах:

| Variable | Value | Description |
|----------|-------|-------------|
| `NEXT_PUBLIC_BACKEND_URL` | `https://test-generator-backend.fly.dev` | Backend API URL |

**Чухал:** `NEXT_PUBLIC_` prefix заавал шаардлагатай (Next.js public variables)

## 🔧 Асуудлыг шийдвэрлэх

### Build алдаа:
```bash
# Local дээр test хийх
npm run build
```

### CORS алдаа:
- Backend дээр `FRONTEND_URL` зөв тохируулсан эсэхийг шалгах
- Frontend URL-ийг Fly.io secrets дээр нэмэх

### API connection алдаа:
- `NEXT_PUBLIC_BACKEND_URL` зөв тохируулсан эсэхийг шалгах
- Browser console дээр network requests шалгах

## 🎯 Production Checklist

- [ ] Frontend Vercel дээр deploy хийсэн
- [ ] Frontend URL тэмдэглэсэн
- [ ] Backend Fly.io дээр deploy хийсэн
- [ ] `FRONTEND_URL` Fly.io secrets дээр тохируулсан
- [ ] `NEXT_PUBLIC_BACKEND_URL` Vercel дээр тохируулсан
- [ ] Test хийсэн (PDF upload, MCQ generate)

## 💡 Tips

1. **Preview Deployments**: Vercel preview URL-үүд үүсгэдэг (PR бүрт)
2. **Automatic Deployments**: GitHub push хийхэд автоматаар deploy хийгддэг
3. **Environment Variables**: Production, Preview, Development гэж тусдаа тохируулж болно

## 📞 Тусламж

```bash
# Vercel CLI help
vercel --help

# Project info
vercel ls

# Logs
vercel logs
```


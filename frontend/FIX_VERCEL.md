# 🔧 Vercel Build Error - Шийдэл

## ❌ Асуудал

Vercel root directory-аас build хийж байна, `frontend` folder-ийг олж чадахгүй байна.

**Алдаа:**
```
Running "install" command: `npm install`...
# Root directory дээр package.json байхгүй
```

## ✅ Шийдэл 2 арга

### Арга 1: Root vercel.json ашиглах (Хялбар) ✅

Root folder дээр `vercel.json` файл үүсгэсэн. Энэ нь Vercel-д `frontend` folder-ийг ашиглахыг заана.

**Хийх зүйл:**
1. Root `vercel.json` файл байгаа эсэхийг шалгах
2. Vercel dashboard дээр project-ийг дахин deploy хийх
3. Эсвэл: Vercel Settings → General → Root Directory: `frontend` гэж тохируулах

### Арга 2: Vercel Dashboard дээр Root Directory тохируулах

1. Vercel Dashboard → Project → Settings → General
2. **Root Directory** хэсэг олох
3. `frontend` гэж бичих
4. Save
5. Deployments → Redeploy хийх

## 📝 Алхам алхмаар

### Step 1: Vercel Dashboard дээр

1. [vercel.com/dashboard](https://vercel.com/dashboard) руу оч
2. Project-оо сонгох
3. **Settings** → **General** руу оч
4. Scroll down → **Root Directory** хэсэг олох
5. `frontend` гэж бичих (эсвэл `./frontend`)
6. **Save** дар

### Step 2: Redeploy

1. **Deployments** tab руу оч
2. Latest deployment → **⋯** (three dots) → **Redeploy**
3. Эсвэл: **Deployments** → **Redeploy** button

## 🔍 Шалгах

Deploy хийсний дараа build logs дээр:

```
✅ Running "install" command: `cd frontend && npm install`...
✅ Running "build" command: `cd frontend && npm run build`...
```

Энэ нь зөв ажиллаж байгааг харуулна.

## ⚠️ Хэрэв асуудал үргэлжилвэл

### Option A: Project дахин үүсгэх

1. Vercel Dashboard → **Add New** → **Project**
2. GitHub repo: `Dorjnyam/MSQ` сонгох
3. **Configure Project** хэсэг дээр:
   - **Root Directory**: `frontend` бичих
   - **Framework Preset**: Next.js
4. Deploy

### Option B: vercel.json шалгах

Root folder дээр `vercel.json` байгаа эсэхийг шалгах:

```json
{
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/.next",
  "installCommand": "cd frontend && npm install"
}
```

## ✅ Бэлэн!

Одоо Vercel зөв folder-оос build хийх ёстой.


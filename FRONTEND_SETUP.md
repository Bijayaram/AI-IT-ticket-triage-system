# Frontend Setup Guide - Next.js + React

## Overview
The frontend has been redesigned using Next.js 14 with React, TypeScript, and Tailwind CSS, replacing the previous Streamlit apps.

## Project Structure

```
frontend/
├── app/                          # Next.js App Router
│   ├── layout.tsx               # Root layout
│   ├── globals.css              # Global styles + Tailwind
│   ├── page.tsx                 # Customer Portal Homepage ✅
│   ├── track/                   # Track Tickets Page
│   │   └── page.tsx
│   └── manager/                 # Manager Dashboard
│       ├── page.tsx             # Dashboard Login & Overview
│       ├── approvals/           # Pending Approvals Page
│       │   └── page.tsx
│       └── tickets/             # All Tickets Page
│           └── page.tsx
├── components/                   # Reusable Components
│   ├── TicketCard.tsx
│   ├── MetricCard.tsx
│   ├── StatusBadge.tsx
│   └── Chart.tsx
├── lib/                         # Utilities & API Client
│   ├── api.ts                   # API Client ✅
│   ├── types.ts                 # TypeScript Types ✅
│   └── utils.ts                 # Helper Functions
├── public/                      # Static Assets
│   └── favicon.ico
├── package.json                 # Dependencies ✅
├── tsconfig.json                # TypeScript Config ✅
├── tailwind.config.ts           # Tailwind Config ✅
├── next.config.mjs              # Next.js Config ✅
├── postcss.config.mjs           # PostCSS Config ✅
└── .env.local.example           # Environment Variables ✅
```

## Installation Steps

### 1. Install Dependencies

```bash
cd frontend
npm install
```

This installs:
- **Next.js 14**: React framework
- **React 18**: UI library
- **TypeScript**: Type safety
- **Tailwind CSS**: Utility-first CSS
- **Axios**: HTTP client
- **React Hot Toast**: Toast notifications
- **Recharts**: Chart library
- **Lucide React**: Icon library

### 2. Configure Environment

Create `.env.local`:

```bash
cp .env.local.example .env.local
```

Edit `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_MANAGER_PASSWORD=admin123
```

### 3. Start Development Server

```bash
npm run dev
```

The app will be available at:
- **Customer Portal**: http://localhost:3000
- **Track Tickets**: http://localhost:3000/track
- **Manager Dashboard**: http://localhost:3000/manager

### 4. Build for Production

```bash
npm run build
npm start
```

## Features

### Customer Portal (/)

**Features:**
- Clean, tutorial-style UI inspired by modern SaaS applications
- Step-by-step ticket submission form
- Real-time AI triage with instant feedback
- Success page with ticket details
- Priority indicators and status updates

**Tech Stack:**
- Next.js App Router
- React Server Components for performance
- Client-side form handling
- Tailwind CSS for styling
- React Hot Toast for notifications

### Track Tickets (/track)

**Features:**
- Email-based ticket lookup
- Ticket history and status
- Response viewing
- Clean card-based design

### Manager Dashboard (/manager)

**Features:**
- Secure password authentication
- Real-time KPI metrics
- Interactive charts (Recharts)
- Pending approvals management
- All tickets view with filters
- Dark professional theme

**Pages:**
1. **/manager** - Login & Overview Dashboard
2. **/manager/approvals** - Pending Critical Approvals
3. **/manager/tickets** - All Tickets with Filters

## API Integration

The frontend communicates with the FastAPI backend via the API client (`lib/api.ts`).

### API Client Features:
- Type-safe requests using TypeScript
- Axios for HTTP client
- Error handling
- Request/response interceptors (ready for auth tokens)

### Example Usage:

```typescript
import { createTicket, triageTicket } from '@/lib/api';

// Create ticket
const formData = new FormData();
formData.append('subject', 'VPN Issue');
formData.append('body', 'Cannot connect');
formData.append('submitter_name', 'John');
formData.append('submitter_email', 'john@company.com');

const ticket = await createTicket(formData);

// Triage ticket
const result = await triageTicket(ticket.id, { run_draft: true });
```

## Styling

### Tailwind CSS Configuration

Custom theme extends with:
- **Primary colors**: Cyan/Teal gradient (#0891b2, #06b6d4, #22d3ee)
- **Dark colors**: Navy/Purple gradient (#1a1d2e, #2d1b4e)
- **Custom utilities**:
  - `.glass` - Glassmorphism effect
  - `.gradient-bg` - Cyan gradient background
  - `.gradient-dark` - Dark purple gradient

### Design System:

**Customer Portal:**
- Cyan/Blue gradient background
- White glassmorphism cards
- Clean, modern typography (Inter font)
- Step-by-step numbered sections
- Large CTAs with icons

**Manager Dashboard:**
- Dark purple gradient background
- White metric cards with shadows
- Professional charts
- Color-coded status indicators
- Minimal, data-focused design

## Components (To Be Created)

### MetricCard.tsx
Displays KPI metrics with icons and trend indicators.

```typescript
interface MetricCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  change?: string;
  changeType?: 'positive' | 'negative';
}
```

### StatusBadge.tsx
Color-coded status badges for tickets.

```typescript
interface StatusBadgeProps {
  status: TicketStatus;
}
```

### TicketCard.tsx
Expandable ticket card with details.

```typescript
interface TicketCardProps {
  ticket: Ticket;
  onSelect?: (id: number) => void;
}
```

### Chart.tsx
Wrapper for Recharts components with consistent styling.

## Next Steps to Complete Frontend

### High Priority:

1. **Create Track Page** (`app/track/page.tsx`)
   - Email input form
   - List user's tickets
   - View ticket details and responses

2. **Create Manager Dashboard** (`app/manager/page.tsx`)
   - Login form
   - Dashboard overview with charts
   - KPI metrics

3. **Create Approvals Page** (`app/manager/approvals/page.tsx`)
   - List pending approvals
   - View ticket details
   - Approve/Reject forms

4. **Create All Tickets Page** (`app/manager/tickets/page.tsx`)
   - Filters (status, department, priority)
   - Ticket list
   - Pagination

5. **Create Shared Components**
   - MetricCard
   - StatusBadge
   - TicketCard
   - Loading spinners
   - Error boundaries

### Medium Priority:

6. **Add Authentication**
   - JWT tokens
   - Protected routes
   - Session management

7. **Add Real-time Updates**
   - WebSocket connection
   - Live status updates
   - Notifications

8. **Add Charts**
   - Bar chart for departments
   - Line chart for trends
   - Donut chart for status distribution

### Low Priority:

9. **Add Dark Mode Toggle**
10. **Add Export Functionality**
11. **Add Advanced Filters**
12. **Add Bulk Operations**

## Testing

### Run Linter:
```bash
npm run lint
```

### Build Check:
```bash
npm run build
```

### Type Check:
```bash
npx tsc --noEmit
```

## Deployment

### Vercel (Recommended):
```bash
vercel
```

### Docker:
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

### Environment Variables for Production:
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_MANAGER_PASSWORD=<secure-password>
```

## Performance Optimizations

1. **Image Optimization**: Use Next.js Image component
2. **Code Splitting**: Automatic with App Router
3. **Server Components**: Default in Next.js 14
4. **Caching**: Configure `fetch` caching
5. **Bundle Size**: Analyze with `@next/bundle-analyzer`

## Security Considerations

1. **API Keys**: Never expose in client code
2. **CSRF Protection**: Implement CSRF tokens
3. **Rate Limiting**: Client-side + backend
4. **Input Validation**: Validate all user inputs
5. **XSS Protection**: React escapes by default
6. **Content Security Policy**: Configure in `next.config.mjs`

## Browser Support

- Chrome (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
- Edge (latest 2 versions)

## Troubleshooting

### Issue: API connection refused
**Solution**: Ensure backend is running on http://localhost:8000

### Issue: Module not found
**Solution**: Run `npm install` in frontend directory

### Issue: Port 3000 already in use
**Solution**: Use different port: `PORT=3001 npm run dev`

### Issue: Environment variables not loading
**Solution**: Restart dev server after changing `.env.local`

---

**Status**: ✅ Core structure created  
**Next**: Complete remaining pages and components  
**Last Updated**: 2026-02-03

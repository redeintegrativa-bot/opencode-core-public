---
name: ui-ux-system
description: Comprehensive UI/UX Design System for building accessible, animated, and modern web interfaces. Synthesizes best practices from shadcn/ui, Magic UI, Framer Motion, Radix Primitives, Lucide/Tabler icons, Tremor dashboards, XYFlow, tldraw, Novel editor, and AI streaming patterns from llm-ui and CopilotKit.
user-invocable: true
allowed-tools:
  - bash
  - read
  - write
  - edit
  - glob
  - grep
  - webfetch
---

# UI/UX Design System Skill

A comprehensive design system skill for building production-quality web interfaces with accessibility, animation, and modern UX patterns.

---

## 1. Tech Stack Standards

### Tailwind CSS

- **Utility-first**: Use Tailwind classes directly in markup; avoid custom CSS unless necessary
- **Design tokens**: Define theme values in `tailwind.config.ts` under `theme.extend`
- **Dark mode**: Use `dark:` prefix with `class` strategy for toggle support
- **Responsive**: Mobile-first breakpoints: `sm:` (640), `md:` (768), `lg:` (1024), `xl:` (1280), `2xl:` (1536)

```ts
// tailwind.config.ts
import type { Config } from "tailwindcss"

const config: Config = {
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}

export default config
```

### CSS Variables (globals.css)

```css
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --primary: 210 40% 98%;
    --primary-foreground: 222.2 47.4% 11.2%;
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 212.7 26.8% 83.9%;
  }
}
```

### Radix UI

- Use `@radix-ui/react-*` primitives for accessible behavior
- Compose with `cva` (class-variance-authority) for variant management
- Prefer unstyled primitives: `Dialog`, `Popover`, `DropdownMenu`, `Select`, `Tabs`, `Accordion`, `Tooltip`
- Always wrap in `Provider` for context

```bash
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu @radix-ui/react-select @radix-ui/react-tabs @radix-ui/react-tooltip @radix-ui/react-accordion @radix-ui/react-popover @radix-ui/react-slot
```

### Framer Motion

- Import from `framer-motion` (or `motion/react` for newer versions)
- Use `motion.div` for animated containers
- Use `AnimatePresence` for mount/unmount transitions
- Use `useInView` for scroll-triggered animations
- Use `useReducedMotion()` to respect user preferences

```bash
npm install framer-motion
```

### Magic UI

- Use for animated gradients, particles, beam effects, and spotlight cards
- Available components: `AnimatedGradientText`, `Particles`, `Meteors`, `Globe`, `CardSpotlight`, `GlowingCard`, `AnimatedBeam`, `WordRotate`, `NumberTicker`
- Install from `@magicuidesign/magicui` or copy components

### Icon System (Lucide + Tabler)

- **Lucide React** — primary icon set, tree-shakeable, consistent 24x24 stroke style
- **Tabler Icons** — secondary set for additional coverage, similar stroke style
- Always use `aria-hidden="true"` on decorative icons
- For interactive icons, wrap in `<button>` with `aria-label`

```bash
npm install lucide-react @tabler/icons-react
```

```tsx
import { Home, Settings, User } from "lucide-react"
import { IconDashboard, IconSettings } from "@tabler/icons-react"

// Usage
<Settings className="h-5 w-5" aria-hidden="true" />
```

---

## 2. Component Patterns

### Button Variants

```tsx
import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp className={buttonVariants({ variant, size, className })} ref={ref} {...props} />
    )
  }
)
Button.displayName = "Button"
```

### Card Patterns

```tsx
import * as React from "react"

const Card = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={`rounded-lg border bg-card text-card-foreground shadow-sm ${className}`} {...props} />
  )
)
Card.displayName = "Card"

const CardHeader = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={`flex flex-col space-y-1.5 p-6 ${className}`} {...props} />
  )
)

const CardTitle = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => (
    <h3 ref={ref} className={`text-2xl font-semibold leading-none tracking-tight ${className}`} {...props} />
  )
)

const CardDescription = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLParagraphElement>>(
  ({ className, ...props }, ref) => (
    <p ref={ref} className={`text-sm text-muted-foreground ${className}`} {...props} />
  )
)

const CardContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={`p-6 pt-0 ${className}`} {...props} />
  )
)

const CardFooter = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={`flex items-center p-6 pt-0 ${className}`} {...props} />
  )
)
```

### Form Patterns

```tsx
import * as React from "react"
import * as LabelPrimitive from "@radix-ui/react-label"
import { cva } from "class-variance-authority"

const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, type, ...props }, ref) => (
    <input
      type={type}
      className={`flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
      ref={ref}
      {...props}
    />
  )
)

const Select = React.forwardRef<HTMLSelectElement, React.SelectHTMLAttributes<HTMLSelectElement>>(
  ({ className, children, ...props }, ref) => (
    <select
      className={`flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
      ref={ref}
      {...props}
    >
      {children}
    </select>
  )
)

// Checkbox with Radix
import * as CheckboxPrimitive from "@radix-ui/react-checkbox"
import { Check } from "lucide-react"

const Checkbox = React.forwardRef<
  React.ElementRef<typeof CheckboxPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof CheckboxPrimitive.Root>
>(({ className, ...props }, ref) => (
  <CheckboxPrimitive.Root
    ref={ref}
    className={`peer h-4 w-4 shrink-0 rounded-sm border border-primary ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground ${className}`}
    {...props}
  >
    <CheckboxPrimitive.Indicator className="flex items-center justify-center text-current">
      <Check className="h-4 w-4" />
    </CheckboxPrimitive.Indicator>
  </CheckboxPrimitive.Root>
))
```

### Modal/Dialog Patterns

```tsx
import * as React from "react"
import * as DialogPrimitive from "@radix-ui/react-dialog"
import { X } from "lucide-react"

const Dialog = DialogPrimitive.Root
const DialogTrigger = DialogPrimitive.Trigger
const DialogPortal = DialogPrimitive.Portal
const DialogClose = DialogPrimitive.Close

const DialogOverlay = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Overlay>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Overlay>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Overlay
    ref={ref}
    className={`fixed inset-0 z-50 bg-black/80 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 ${className}`}
    {...props}
  />
))

const DialogContent = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Content>
>(({ className, children, ...props }, ref) => (
  <DialogPortal>
    <DialogOverlay />
    <DialogPrimitive.Content
      ref={ref}
      className={`fixed left-[50%] top-[50%] z-50 grid w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border bg-background p-6 shadow-lg duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%] sm:rounded-lg ${className}`}
      {...props}
    >
      {children}
      <DialogPrimitive.Close className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2">
        <X className="h-4 w-4" />
      </DialogPrimitive.Close>
    </DialogPrimitive.Content>
  </DialogPortal>
))
```

### Navigation Patterns

```tsx
// Sidebar navigation
const Sidebar = () => (
  <aside className="flex h-screen w-64 flex-col border-r bg-muted/40">
    <div className="flex h-14 items-center border-b px-4 font-semibold">Logo</div>
    <nav className="flex-1 space-y-1 p-2" aria-label="Main navigation">
      <a href="/" className="flex items-center gap-3 rounded-lg bg-primary/10 px-3 py-2 text-sm font-medium text-primary">
        <Home className="h-4 w-4" />
        Dashboard
      </a>
      <a href="/settings" className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-muted hover:text-foreground transition-colors">
        <Settings className="h-4 w-4" />
        Settings
      </a>
    </nav>
  </aside>
)

// Topbar with responsive mobile menu
const Topbar = () => (
  <header className="sticky top-0 z-40 flex h-14 items-center gap-4 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 px-4">
    <Button variant="ghost" size="icon" className="md:hidden" aria-label="Toggle menu">
      <Menu className="h-5 w-5" />
    </Button>
    <nav className="hidden md:flex items-center gap-4 text-sm font-medium" aria-label="Tabs">
      <a href="/overview" className="text-foreground">Overview</a>
      <a href="/analytics" className="text-muted-foreground hover:text-foreground transition-colors">Analytics</a>
      <a href="/reports" className="text-muted-foreground hover:text-foreground transition-colors">Reports</a>
    </nav>
  </header>
)
```

### Data Display

```tsx
// Table with sorting
const DataTable = ({ columns, data }) => (
  <div className="rounded-md border">
    <table className="w-full caption-bottom text-sm">
      <thead className="[&_tr]:border-b">
        <tr className="border-b transition-colors hover:bg-muted/50">
          {columns.map((col) => (
            <th key={col.key} className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
              {col.label}
            </th>
          ))}
        </tr>
      </thead>
      <tbody className="[&_tr:last-child]:border-0">
        {data.map((row, i) => (
          <tr key={i} className="border-b transition-colors hover:bg-muted/50">
            {columns.map((col) => (
              <td key={col.key} className="p-4 align-middle">{row[col.key]}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
)

// Grid layout
const DataGrid = ({ children }) => (
  <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
    {children}
  </div>
)
```

### Feedback Patterns

```tsx
// Toast notification
import { toast } from "sonner" // or use @radix-ui/react-toast

const showToast = () => toast.success("Changes saved", { description: "Your settings have been updated." })

// Alert component
const Alert = ({ variant = "default", title, description }) => {
  const variants = {
    default: "bg-background text-foreground border",
    destructive: "border-destructive/50 text-destructive dark:border-destructive [&>svg]:text-destructive",
    success: "border-green-500/50 text-green-700 dark:text-green-400 [&>svg]:text-green-500",
  }
  return (
    <div role="alert" className={`relative w-full rounded-lg border p-4 ${variants[variant]}`}>
      {title && <h5 className="mb-1 font-medium leading-none tracking-tight">{title}</h5>}
      {description && <div className="text-sm [&_p]:leading-relaxed">{description}</div>}
    </div>
  )
}

// Skeleton loading
const Skeleton = ({ className }) => (
  <div className={`animate-pulse rounded-md bg-muted ${className}`} />
)

// Usage
<div className="space-y-2">
  <Skeleton className="h-4 w-[250px]" />
  <Skeleton className="h-4 w-[200px]" />
</div>
```

---

## 3. AI/Streaming UI Patterns

### Streaming Text Display

```tsx
"use client"

import { useState, useEffect } from "react"

interface StreamingTextProps {
  text: string
  speed?: number
  onComplete?: () => void
  className?: string
}

function StreamingText({ text, speed = 20, onComplete, className }: StreamingTextProps) {
  const [displayed, setDisplayed] = useState("")
  const [isComplete, setIsComplete] = useState(false)

  useEffect(() => {
    setDisplayed("")
    setIsComplete(false)
    let i = 0
    const timer = setInterval(() => {
      if (i < text.length) {
        setDisplayed(text.slice(0, i + 1))
        i++
      } else {
        clearInterval(timer)
        setIsComplete(true)
        onComplete?.()
      }
    }, speed)
    return () => clearInterval(timer)
  }, [text, speed])

  return (
    <div className={className}>
      {displayed}
      {!isComplete && <span className="inline-block w-0.5 h-4 bg-foreground animate-pulse ml-0.5" />}
    </div>
  )
}
```

### Chat Interface

```tsx
import { useState, useRef, useEffect } from "react"
import { Send, User, Bot } from "lucide-react"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
}

function ChatInterface({ onSendMessage }: { onSendMessage: (msg: string) => void }) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" })
  }, [messages])

  return (
    <div className="flex flex-col h-[600px] border rounded-lg">
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : ""}`}>
            {msg.role === "assistant" && (
              <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center shrink-0">
                <Bot className="h-4 w-4 text-primary-foreground" />
              </div>
            )}
            <div className={`rounded-lg px-4 py-2 max-w-[80%] ${
              msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"
            }`}>
              <p className="text-sm">{msg.content}</p>
            </div>
            {msg.role === "user" && (
              <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center shrink-0">
                <User className="h-4 w-4" />
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-3">
            <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center shrink-0">
              <Bot className="h-4 w-4 text-primary-foreground" />
            </div>
            <div className="rounded-lg px-4 py-2 bg-muted">
              <div className="flex gap-1">
                <span className="h-2 w-2 rounded-full bg-foreground/40 animate-bounce [animation-delay:0ms]" />
                <span className="h-2 w-2 rounded-full bg-foreground/40 animate-bounce [animation-delay:150ms]" />
                <span className="h-2 w-2 rounded-full bg-foreground/40 animate-bounce [animation-delay:300ms]" />
              </div>
            </div>
          </div>
        )}
      </div>
      <div className="border-t p-4">
        <form onSubmit={(e) => { e.preventDefault(); if (input.trim()) { onSendMessage(input); setInput(""); } }} className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 rounded-md border bg-background px-3 py-2 text-sm"
            disabled={isLoading}
          />
          <Button type="submit" size="icon" disabled={!input.trim() || isLoading}>
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </div>
    </div>
  )
}
```

### Copilot Sidebar Pattern

```tsx
import { useState } from "react"
import { PanelRightClose, PanelRightOpen, Sparkles } from "lucide-react"

function CopilotSidebar({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="flex h-screen">
      <main className="flex-1 overflow-auto">{children}</main>
      <aside className={`border-l transition-all duration-300 ${isOpen ? "w-96" : "w-0"}`}>
        {isOpen && (
          <div className="flex flex-col h-full w-96">
            <div className="flex items-center justify-between border-b p-4">
              <div className="flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-primary" />
                <span className="font-semibold text-sm">AI Copilot</span>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setIsOpen(false)}>
                <PanelRightClose className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex-1 overflow-y-auto p-4">
              <ChatInterface onSendMessage={(msg) => console.log(msg)} />
            </div>
          </div>
        )}
      </aside>
      {!isOpen && (
        <Button variant="outline" size="icon" className="fixed right-4 bottom-4 rounded-full shadow-lg" onClick={() => setIsOpen(true)}>
          <PanelRightOpen className="h-4 w-4" />
        </Button>
      )}
    </div>
  )
}
```

### Loading States for AI Responses

```tsx
// Streaming indicator with progress
function StreamingIndicator({ label = "Thinking" }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 text-sm text-muted-foreground">
      <div className="relative h-4 w-4">
        <Sparkles className="h-4 w-4 animate-spin" />
      </div>
      <span>{label}...</span>
    </div>
  )
}

// Block-level skeleton for AI content
function AISkeleton() {
  return (
    <div className="space-y-3 animate-pulse">
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-[90%]" />
      <Skeleton className="h-4 w-[75%]" />
      <Skeleton className="h-4 w-[85%]" />
    </div>
  )
}
```

---

## 4. Animation Guidelines

### Page Transitions

```tsx
import { motion, AnimatePresence } from "framer-motion"
import { useReducedMotion } from "framer-motion"

const pageVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
}

function PageTransition({ children }: { children: React.ReactNode }) {
  const shouldReduce = useReducedMotion()

  return (
    <AnimatePresence mode="wait">
      <motion.div
        variants={shouldReduce ? {} : pageVariants}
        initial={shouldReduce ? false : "initial"}
        animate="animate"
        exit="exit"
        transition={{ duration: 0.2, ease: "easeInOut" }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  )
}
```

### Scroll-Triggered Reveals

```tsx
import { motion, useInView } from "framer-motion"
import { useRef } from "react"

function RevealOnScroll({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-100px" })

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 30 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
      transition={{ duration: 0.5, delay, ease: "easeOut" }}
    >
      {children}
    </motion.div>
  )
}

// Staggered list reveal
function StaggeredList({ items }: { items: string[] }) {
  return (
    <motion.ul initial="hidden" animate="visible" variants={{ visible: { transition: { staggerChildren: 0.1 } } }}>
      {items.map((item, i) => (
        <motion.li
          key={i}
          variants={{ hidden: { opacity: 0, x: -20 }, visible: { opacity: 1, x: 0 } }}
          transition={{ duration: 0.3 }}
        >
          {item}
        </motion.li>
      ))}
    </motion.ul>
  )
}
```

### Hover Micro-interactions

```tsx
// Button hover scale
<motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }} className="...">
  Click me
</motion.button>

// Card hover lift
<motion.div whileHover={{ y: -4, boxShadow: "0 10px 40px rgba(0,0,0,0.1)" }} transition={{ duration: 0.2 }}>
  <Card>...</Card>
</motion.div>

// Icon spin on hover
<motion.div whileHover={{ rotate: 180 }} transition={{ duration: 0.3 }}>
  <Settings className="h-5 w-5" />
</motion.div>
```

### Loading Animations

```tsx
// Pulse ring
const PulseLoader = () => (
  <div className="relative h-8 w-8">
    <div className="absolute inset-0 rounded-full border-2 border-primary/20" />
    <div className="absolute inset-0 rounded-full border-2 border-primary border-t-transparent animate-spin" />
  </div>
)

// Dots loader
const DotsLoader = () => (
  <div className="flex gap-1.5">
    {[0, 1, 2].map((i) => (
      <motion.div
        key={i}
        className="h-2 w-2 rounded-full bg-primary"
        animate={{ y: [0, -8, 0] }}
        transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.15 }}
      />
    ))}
  </div>
)

// Bar loader
const BarLoader = () => (
  <div className="h-1 w-full overflow-hidden rounded-full bg-muted">
    <motion.div
      className="h-full bg-primary"
      initial={{ x: "-100%" }}
      animate={{ x: "100%" }}
      transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
    />
  </div>
)
```

### Reduced Motion Support

```tsx
import { useReducedMotion } from "framer-motion"

function AnimatedComponent() {
  const shouldReduce = useReducedMotion()

  return (
    <motion.div
      animate={shouldReduce ? { opacity: 1 } : { opacity: 1, y: 0, scale: 1 }}
      initial={shouldReduce ? {} : { opacity: 0, y: 20, scale: 0.95 }}
      transition={shouldReduce ? { duration: 0 } : { duration: 0.3 }}
    >
      Content
    </motion.div>
  )
}
```

Also add to global CSS:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

---

## 5. Accessibility (a11y)

### WCAG 2.1 AA Compliance

- **Color contrast**: Minimum 4.5:1 for normal text, 3:1 for large text (18px+ or 14px bold)
- **Target size**: Interactive elements minimum 44x44px (use `h-11 w-11` or larger)
- **Text resizing**: Support up to 200% zoom without horizontal scroll
- **Color independence**: Never use color alone to convey information — add icons, text, or patterns

```tsx
// Contrast-safe color pairs (dark bg / light text)
const safePairs = {
  primary: { bg: "hsl(222, 47%, 11%)", fg: "hsl(210, 40%, 98%)", ratio: "15.3:1" },
  muted: { bg: "hsl(217, 33%, 18%)", fg: "hsl(215, 20%, 65%)", ratio: "5.2:1" },
  accent: { bg: "hsl(217, 33%, 18%)", fg: "hsl(210, 40%, 98%)", ratio: "10.1:1" },
}
```

### Keyboard Navigation

```tsx
// Focus visible styles (in globals.css)
// .focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2

// Skip to main content link
function SkipLink() {
  return (
    <a href="#main-content" className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-50 focus:rounded-md focus:bg-primary focus:px-4 focus:py-2 focus:text-primary-foreground focus:outline-none">
      Skip to main content
    </a>
  )
}

// Roving tabindex for toolbars
function Toolbar() {
  return (
    <div role="toolbar" aria-label="Formatting" className="flex gap-1">
      <Button tabIndex={0} aria-label="Bold"><Bold /></Button>
      <Button tabIndex={-1} aria-label="Italic"><Italic /></Button>
      <Button tabIndex={-1} aria-label="Underline"><Underline /></Button>
    </div>
  )
}
```

### Screen Reader Support

```tsx
// Visually hidden text
const VisuallyHidden = ({ children }: { children: React.ReactNode }) => (
  <span className="sr-only">{children}</span>
)

// Live regions for dynamic content
function LiveStatus({ message }: { message: string }) {
  return (
    <div role="status" aria-live="polite" className="sr-only">
      {message}
    </div>
  )
}

// Announce page changes
function PageAnnouncer({ title }: { title: string }) {
  return (
    <div role="status" aria-live="assertive" aria-atomic="true" className="sr-only">
      Page loaded: {title}
    </div>
  )
)
```

### Focus Management

```tsx
import { useCallback, useRef } from "react"

// Trap focus in modal
function useFocusTrap() {
  const containerRef = useRef<HTMLDivElement>(null)

  const trapFocus = useCallback((e: React.KeyboardEvent) => {
    if (e.key !== "Tab" || !containerRef.current) return
    const focusable = containerRef.current.querySelectorAll<HTMLElement>(
      'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
    )
    const first = focusable[0]
    const last = focusable[focusable.length - 1]
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus() }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus() }
  }, [])

  return { containerRef, trapFocus }
}

// Restore focus after modal close
function useFocusRestore() {
  const previousFocus = useRef<HTMLElement | null>(null)

  const saveFocus = () => { previousFocus.current = document.activeElement as HTMLElement }
  const restoreFocus = () => { previousFocus.current?.focus() }

  return { saveFocus, restoreFocus }
}
```

### ARIA Patterns

```tsx
// Disclosure / Accordion
<button aria-expanded={isOpen} aria-controls="panel-1" onClick={toggle}>
  Section Title
</button>
<div id="panel-1" role="region" aria-labelledby="heading-1" hidden={!isOpen}>
  Content
</div>

// Tabs
<div role="tablist" aria-label="Settings">
  <button role="tab" aria-selected={active === "general"} aria-controls="panel-general" id="tab-general">General</button>
  <button role="tab" aria-selected={active === "advanced"} aria-controls="panel-advanced" id="tab-advanced">Advanced</button>
</div>
<div role="tabpanel" id="panel-general" aria-labelledby="tab-general" hidden={active !== "general"}>...</div>
<div role="tabpanel" id="panel-advanced" aria-labelledby="tab-advanced" hidden={active !== "advanced"}>...</div>

// Alert / Status
<div role="alert" className="rounded-md bg-destructive/10 p-4 text-destructive">
  Error: Invalid input
</div>
```

---

## 6. Dashboard Patterns

### Layout Grid

```tsx
// 12-column responsive grid
function DashboardGrid({ children }: { children: React.ReactNode }) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-12">
      {children}
    </div>
  )
}

// Usage
<DashboardGrid>
  <div className="col-span-1 sm:col-span-2 lg:col-span-4 xl:col-span-8">
    <ChartCard />
  </div>
  <div className="col-span-1 sm:col-span-2 lg:col-span-2 xl:col-span-4">
    <StatsCard />
  </div>
  <div className="col-span-1 sm:col-span-2 lg:col-span-4 xl:col-span-6">
    <DataTable />
  </div>
  <div className="col-span-1 sm:col-span-2 lg:col-span-4 xl:col-span-6">
    <ActivityFeed />
  </div>
</DashboardGrid>
```

### Chart Containers

```tsx
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { MoreHorizontal } from "lucide-react"

function ChartCard({ title, description, children, actions }: {
  title: string
  description?: string
  children: React.ReactNode
  actions?: React.ReactNode
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div>
          <CardTitle className="text-sm font-medium">{title}</CardTitle>
          {description && <CardDescription>{description}</CardDescription>}
        </div>
        {actions || (
          <Button variant="ghost" size="icon">
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        )}
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  )
}
```

### Stats Cards

```tsx
function StatsCard({ title, value, change, icon: Icon }: {
  title: string
  value: string
  change?: { value: number; trend: "up" | "down" }
  icon: React.ElementType
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {change && (
          <p className={`text-xs ${change.trend === "up" ? "text-green-600" : "text-red-600"}`}>
            {change.trend === "up" ? "+" : ""}{change.value}% from last month
          </p>
        )}
      </CardContent>
    </Card>
  )
}
```

### Data Tables with Sorting/Filtering

```tsx
import { useState, useMemo } from "react"
import { ArrowUpDown, ChevronDown, Search, Filter } from "lucide-react"

interface Column<T> {
  key: keyof T & string
  label: string
  sortable?: boolean
  filterable?: boolean
  render?: (value: T[keyof T], row: T) => React.ReactNode
}

function SortableDataTable<T extends Record<string, unknown>>({ columns, data }: {
  columns: Column<T>[]
  data: T[]
}) {
  const [sortKey, setSortKey] = useState<string | null>(null)
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc")
  const [filter, setFilter] = useState("")
  const [columnFilters, setColumnFilters] = useState<Record<string, string>>({})

  const filteredData = useMemo(() => {
    let result = data
    if (filter) {
      result = result.filter((row) =>
        Object.values(row).some((v) => String(v).toLowerCase().includes(filter.toLowerCase()))
      )
    }
    Object.entries(columnFilters).forEach(([key, val]) => {
      if (val) result = result.filter((row) => String(row[key]).toLowerCase().includes(val.toLowerCase()))
    })
    if (sortKey) {
      result = [...result].sort((a, b) => {
        const aVal = a[sortKey]
        const bVal = b[sortKey]
        if (aVal < bVal) return sortDir === "asc" ? -1 : 1
        if (aVal > bVal) return sortDir === "asc" ? 1 : -1
        return 0
      })
    }
    return result
  }, [data, filter, columnFilters, sortKey, sortDir])

  const toggleSort = (key: string) => {
    if (sortKey === key) setSortDir(sortDir === "asc" ? "desc" : "asc")
    else { setSortKey(key); setSortDir("asc") }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input placeholder="Search..." value={filter} onChange={(e) => setFilter(e.target.value)} className="pl-9" />
        </div>
      </div>
      <div className="rounded-md border">
        <table className="w-full caption-bottom text-sm">
          <thead className="[&_tr]:border-b">
            <tr>
              {columns.map((col) => (
                <th key={col.key} className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">
                  {col.sortable ? (
                    <button onClick={() => toggleSort(col.key)} className="flex items-center gap-1 hover:text-foreground">
                      {col.label}
                      <ArrowUpDown className="h-3 w-3" />
                    </button>
                  ) : col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="[&_tr:last-child]:border-0">
            {filteredData.map((row, i) => (
              <tr key={i} className="border-b transition-colors hover:bg-muted/50">
                {columns.map((col) => (
                  <td key={col.key} className="p-4 align-middle">
                    {col.render ? col.render(row[col.key], row) : String(row[col.key] ?? "")}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="text-sm text-muted-foreground">
        Showing {filteredData.length} of {data.length} results
      </div>
    </div>
  )
}
```

### Real-Time Updates

```tsx
import { useEffect, useState } from "react"

function useRealtimeData<T>(url: string, interval = 5000) {
  const [data, setData] = useState<T | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(url)
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        setData(await res.json())
        setIsLoading(false)
      } catch (err) {
        setError(err as Error)
      }
    }
    fetchData()
    const timer = setInterval(fetchData, interval)
    return () => clearInterval(timer)
  }, [url, interval])

  return { data, isLoading, error }
}

// Live stats with animated number
function LiveStat({ value, label }: { value: number; label: string }) {
  return (
    <div className="text-center">
      <div className="text-3xl font-bold tabular-nums">{value.toLocaleString()}</div>
      <div className="text-sm text-muted-foreground">{label}</div>
    </div>
  )
}
```

---

## 7. Node-Based UI (XYFlow Patterns)

```tsx
import { ReactFlow, Background, Controls, MiniMap, type Node, type Edge } from "@xyflow/react"
import "@xyflow/react/dist/style.css"

const initialNodes: Node[] = [
  { id: "1", position: { x: 0, y: 0 }, data: { label: "Input" }, type: "input" },
  { id: "2", position: { x: 200, y: 0 }, data: { label: "Process" } },
  { id: "3", position: { x: 400, y: 0 }, data: { label: "Output" }, type: "output" },
]

const initialEdges: Edge[] = [
  { id: "e1-2", source: "1", target: "2", animated: true },
  { id: "e2-3", source: "2", target: "3" },
]

function FlowEditor() {
  return (
    <div className="h-[600px] w-full rounded-lg border">
      <ReactFlow nodes={initialNodes} edges={initialEdges} fitView>
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  )
}
```

---

## 8. Canvas Patterns (tldraw-inspired)

```tsx
"use client"

import { useRef, useState, useCallback, useEffect } from "react"

interface Point { x: number; y: number }
interface Shape {
  id: string
  type: "rect" | "circle" | "line"
  points: Point[]
  color: string
}

function CanvasEditor() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [shapes, setShapes] = useState<Shape[]>([])
  const [currentTool, setCurrentTool] = useState<"rect" | "circle" | "line">("rect")
  const [isDrawing, setIsDrawing] = useState(false)
  const [startPoint, setStartPoint] = useState<Point | null>(null)

  const draw = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    ctx.clearRect(0, 0, canvas.width, canvas.height)

    shapes.forEach((shape) => {
      ctx.strokeStyle = shape.color
      ctx.lineWidth = 2
      ctx.beginPath()
      if (shape.type === "rect" && shape.points.length >= 2) {
        const [p1, p2] = shape.points
        ctx.strokeRect(p1.x, p1.y, p2.x - p1.x, p2.y - p1.y)
      } else if (shape.type === "circle" && shape.points.length >= 2) {
        const [p1, p2] = shape.points
        const r = Math.hypot(p2.x - p1.x, p2.y - p1.y)
        ctx.arc(p1.x, p1.y, r, 0, Math.PI * 2)
        ctx.stroke()
      } else if (shape.type === "line" && shape.points.length >= 2) {
        ctx.moveTo(shape.points[0].x, shape.points[0].y)
        shape.points.forEach((p) => ctx.lineTo(p.x, p.y))
        ctx.stroke()
      }
    })
  }, [shapes])

  useEffect(() => { draw() }, [draw])

  return (
    <div className="flex flex-col h-full">
      <div className="flex gap-2 p-2 border-b">
        {(["rect", "circle", "line"] as const).map((tool) => (
          <Button key={tool} variant={currentTool === tool ? "default" : "outline"} size="sm" onClick={() => setCurrentTool(tool)}>
            {tool}
          </Button>
        ))}
      </div>
      <canvas
        ref={canvasRef}
        width={1200}
        height={800}
        className="border cursor-crosshair"
        onMouseDown={(e) => {
          setIsDrawing(true)
          setStartPoint({ x: e.nativeEvent.offsetX, y: e.nativeEvent.offsetY })
        }}
        onMouseUp={(e) => {
          if (startPoint) {
            setShapes((prev) => [...prev, {
              id: crypto.randomUUID(),
              type: currentTool,
              points: [startPoint, { x: e.nativeEvent.offsetX, y: e.nativeEvent.offsetY }],
              color: "#000",
            }])
          }
          setIsDrawing(false)
          setStartPoint(null)
        }}
      />
    </div>
  )
}
```

---

## 9. Rich Text Editor Patterns (Novel-inspired)

```tsx
import { useEditor, EditorContent } from "@tiptap/react"
import StarterKit from "@tiptap/starter-kit"
import Placeholder from "@tiptap/extension-placeholder"
import { Bold, Italic, Code, List, Heading1, Heading2, Quote, Minus } from "lucide-react"

function RichTextEditor({ placeholder = "Start writing..." }: { placeholder?: string }) {
  const editor = useEditor({
    extensions: [
      StarterKit,
      Placeholder.configure({ placeholder }),
    ],
    content: "",
  })

  if (!editor) return null

  const ToolButton = ({ onClick, isActive, children }: { onClick: () => void; isActive?: boolean; children: React.ReactNode }) => (
    <Button type="button" variant={isActive ? "default" : "ghost"} size="sm" onClick={onClick}>
      {children}
    </Button>
  )

  return (
    <div className="rounded-lg border bg-background">
      <div className="flex items-center gap-1 border-b p-1">
        <ToolButton onClick={() => editor.chain().focus().toggleBold().run()} isActive={editor.isActive("bold")}>
          <Bold className="h-4 w-4" />
        </ToolButton>
        <ToolButton onClick={() => editor.chain().focus().toggleItalic().run()} isActive={editor.isActive("italic")}>
          <Italic className="h-4 w-4" />
        </ToolButton>
        <ToolButton onClick={() => editor.chain().focus().toggleCode().run()} isActive={editor.isActive("code")}>
          <Code className="h-4 w-4" />
        </ToolButton>
        <div className="h-6 w-px bg-border" />
        <ToolButton onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()} isActive={editor.isActive("heading", { level: 1 })}>
          <Heading1 className="h-4 w-4" />
        </ToolButton>
        <ToolButton onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()} isActive={editor.isActive("heading", { level: 2 })}>
          <Heading2 className="h-4 w-4" />
        </ToolButton>
        <div className="h-6 w-px bg-border" />
        <ToolButton onClick={() => editor.chain().focus().toggleBulletList().run()} isActive={editor.isActive("bulletList")}>
          <List className="h-4 w-4" />
        </ToolButton>
        <ToolButton onClick={() => editor.chain().focus().toggleBlockquote().run()} isActive={editor.isActive("blockquote")}>
          <Quote className="h-4 w-4" />
        </ToolButton>
        <ToolButton onClick={() => editor.chain().focus().setHorizontalRule().run()}>
          <Minus className="h-4 w-4" />
        </ToolButton>
      </div>
      <EditorContent editor={editor} className="prose max-w-none p-4 min-h-[200px] focus:outline-none [&_.ProseMirror]:focus:outline-none [&_.ProseMirror]:min-h-[200px] [&_.ProseMirror_p.is-editor-empty:first-child::before]:text-muted-foreground [&_.ProseMirror_p.is-editor-empty:first-child::before]:pointer-events-none [&_.ProseMirror_p.is-editor-empty:first-child::before]:h-0 [&_.ProseMirror_p.is-editor-empty:first-child::before]:float-left" />
    </div>
  )
}
```

---

## 10. Quick Start Template

### Project Init

```bash
# Create Next.js project
npx create-next-app@latest my-app --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"

# Install dependencies
cd my-app
npm install framer-motion lucide-react class-variance-authority clsx tailwind-merge
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu @radix-ui/react-select @radix-ui/react-tabs @radix-ui/react-tooltip @radix-ui/react-accordion @radix-ui/react-checkbox @radix-ui/react-popover @radix-ui/react-slot @radix-ui/react-label
npm install -D tailwindcss-animate
```

### Utility Function (lib/utils.ts)

```ts
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

### Basic Layout Structure

```tsx
// app/layout.tsx
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "My App",
  description: "Built with the UI/UX Design System",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
```

```tsx
// components/theme-provider.tsx
"use client"
import { ThemeProvider as NextThemesProvider } from "next-themes"
import { type ThemeProviderProps } from "next-themes/dist/types"

export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>
}
```

### Theme Toggle

```tsx
"use client"
import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  return (
    <Button variant="ghost" size="icon" onClick={() => setTheme(theme === "dark" ? "light" : "dark")} aria-label="Toggle theme">
      <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
      <span className="sr-only">Toggle theme</span>
    </Button>
  )
}
```

### Component Imports

```tsx
// Reusable component imports
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter, DialogClose } from "@/components/ui/dialog"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert } from "@/components/ui/alert"
import { ThemeToggle } from "@/components/theme-provider"

// Icons
import { Home, Settings, User, Search, Bell, ChevronDown, Plus, Trash2, Edit, MoreHorizontal } from "lucide-react"

// Animation
import { motion, AnimatePresence } from "framer-motion"
import { useReducedMotion, useInView } from "framer-motion"

// Utilities
import { cn } from "@/lib/utils"
```

---

## Design Principles

1. **Composition over configuration** — Build complex UIs by composing simple, focused primitives
2. **Accessible by default** — Every component uses correct ARIA attributes, keyboard navigation, and focus management
3. **Motion with purpose** — Animations communicate state changes, not decoration; always respect `prefers-reduced-motion`
4. **Mobile-first responsive** — Design for small screens first, enhance for larger viewports
5. **Dark mode ready** — CSS custom properties enable seamless theme switching
6. **Type-safe** — Full TypeScript support with proper prop types and generic constraints
7. **Performance** — Tree-shakeable icons, lazy-loaded modals, optimized re-renders with `React.memo` and `useMemo`

---

## Referências dos Repositórios

### IA & Streaming UI

| Repository | Use Case | When to Consult |
|---|---|---|
| `shadcn-ui/ui` | Component library, design system patterns, Radix-based UI primitives | Building foundational UI components, styling patterns, or need a proven component architecture |
| `Nutlope/llm-ui` | LLM streaming UI components (typewriter effect, markdown rendering, code blocks) | Implementing real-time LLM output display, streaming text with markdown, or token-by-token rendering |
| `danny-avila/LibreChat` | Multi-model chat interface patterns, conversation management, message history | Building chat UIs that support multiple AI providers, conversation threading, or message persistence |
| `browserbase/stagehand` | Browser automation UI, AI-driven web interaction patterns | Creating interfaces for AI agents that browse the web, form filling, or screen interaction feedback |
| `CopilotKit/CopilotKit` | AI copilot sidebar, in-app AI assistance, context-aware suggestions | Adding an AI assistant panel to existing apps, code suggestion UI, or inline AI actions |

### Animações & Microinterações

| Repository | Use Case | When to Consult |
|---|---|---|
| `magicuidesign/magicui` | Animated gradients, particle effects, shimmer, beam, spotlight components | Need eye-catching decorative effects, animated backgrounds, or attention-grabbing UI accents |
| `framer/motion` | Layout animations, gestures, scroll-triggered animations, page transitions | General-purpose animation library for React — layout shifts, enter/exit, drag, scroll-linked |
| `pmndrs/react-three-fiber` | 3D UI components, WebGL integration, 3D scene rendering in React | Building 3D product viewers, immersive experiences, or data visualization in three dimensions |
| `motion-division/motion` | Advanced motion patterns, spring physics, complex orchestration | Next-gen motion library (Framer Motion successor) — when you need the latest animation primitives |
| `julianshapiro/velocity` | Lightweight jQuery animation engine, CSS color animation | jQuery-based projects needing fast, simple animations without a full React animation library |

### Componentes, Ícones & SaaS

| Repository | Use Case | When to Consult |
|---|---|---|
| `tabler/tabler-icons` | SVG icon set (5000+ icons), consistent stroke style | Need broad icon coverage, Tabler-style icons, or alternative to Lucide for specific icon sets |
| `lucide-icons/lucide` | Feather icons fork, tree-shakable, 24x24 stroke icons | Primary icon set for most projects — clean, minimal, well-maintained, React-friendly |
| `radix-ui/primitives` | Accessible, unstyled UI primitives (dialogs, menus, selects, tooltips) | Building accessible components from scratch, need headless UI with correct ARIA behavior |
| `vercel/commerce` | Next.js e-commerce boilerplate, storefront patterns | Building online stores, product pages, cart/checkout flows with Next.js |
| `saasfly/saasfly` | Full-stack SaaS template (auth, billing, i18n, multi-tenancy) | Scaffolding a SaaS product — includes auth, payments, subscriptions, and localization |

### Canvas, Dashboards & Editores

| Repository | Use Case | When to Consult |
|---|---|---|
| `xyflow/xyflow` | Node-based flow editors (React Flow), drag-and-drop node graphs | Building workflow builders, diagram editors, pipeline visualizers, or node-based UIs |
| `tldraw/tldraw` | Infinite canvas, drawing tools, whiteboard functionality | Creating collaborative whiteboards, annotation tools, or infinite zoom canvas experiences |
| `novel-bms/novel` | Notion-like rich text editor, block-based editing, slash commands | Building content editors with block-based editing, slash menus, and collaborative features |
| `tremorlabs/tremor` | Dashboard components (charts, tables, KPIs, sparklines) | Rapid dashboard building with pre-built data visualization and metric display components |
| `tremorlabs/tremor-raw` | Unstyled dashboard primitives, headless chart/table components | Need dashboard primitives without Tailwind opinions — bring your own styling |

---

## Quick Reference Matrix

| Task | Recommended Repos |
|---|---|
| Need a chat interface? | `danny-avila/LibreChat` + `Nutlope/llm-ui` + `CopilotKit/CopilotKit` |
| Need animations? | `framer/motion` + `magicuidesign/magicui` + `julianshapiro/velocity` |
| Need a dashboard? | `tremorlabs/tremor` + `xyflow/xyflow` |
| Need a canvas/editor? | `tldraw/tldraw` + `novel-bms/novel` + `xyflow/xyflow` |
| Need icons? | `lucide-icons/lucide` + `tabler/tabler-icons` |
| Need accessible components? | `radix-ui/primitives` |
| Need SaaS boilerplate? | `saasfly/saasfly` + `vercel/commerce` |
| Need 3D/visual effects? | `pmndrs/react-three-fiber` |

---

# DESIGN HUB — Módulo de Design & Interface (v1.0)

> Este hub transforma a skill em referência de **design com intenção**, não apenas código.
> Orienta decisões visuais, tendências 2026, landing pages, gate de qualidade, e **quando acionar outros especialistas e repos** do ecossistema.
> Idioma: PT-BR.

---

## 11. Princípios de Design Visual

Regras que separam um site "funciona" de um site "parece feito por um designer".

### 11.1 Hierarquia Visual
- **1 ideia por seção** — cada bloco comunica UMA mensagem principal.
- **Escala tipográfica clara** — Hero 64–96px, título de seção 36–48px, corpo 16–18px, caption 13–14px.
- **Peso > cor para hierarquia** — primeiro diferença de tamanho/weight; cor é reforço.
- **Leitura em F/Z** — elemento mais importante no topo-esquerda (F) ou no centro (Z).

### 11.2 Tipografia (o ativo nº 1 em 2026)
- **Escolha display + body pairing** — uma fonte display forte (ex: Space Grotesk, Sora, Clash Display) + uma body legível (Inter, Manrope).
- **Evite Inter/Roboto "for everything"** — paletas 100% default parecem templates.
- **Tracking**: headings levemente tighter (`-0.02em`), body normal.
- **Line-height**: 1.1–1.2 em headings, 1.6–1.7 em parágrafos.
- **Type scale consistente** via design tokens (não font-size soltos).

### 11.3 Cor
- **Base neutra** (branco / preto / tons de cinza) + **1 cor de destaque saturada** (electric blue, lime, burnt orange) — não paletas tímidas.
- **Contraste WCAG**: 4.5:1 texto normal, 3:1 texto grande.
- **Nunca cor como único sinal** — sempre acompanhe com ícone/texto/padrão.
- **Dark mode**: preto `#0a0b0c`–`#121317` (não `#000` puro), superfícies elevadas um tom acima.

### 11.4 Espaçamento & Ritmo
- **Escala de 8px** (`4, 8, 12, 16, 24, 32, 48, 64, 96`).
- **Seções grandes com respiro** — padding vertical generoso (`py-24` / `py-32`).
- **Consistência**: o mesmo espaçamento significa a mesma relação em todo o site.

### 11.5 Motion com Propósito
- **Só anima transform/opacity** — nunca `width/height/top/left` (custa layout).
- **1–2 reveals por scroll, cirúrgicos** — não animar tudo.
- **`prefers-reduced-motion` obrigatório** — usuário com redução = zero animação.
- **Duração** 200–500ms, easing `ease-out`; micro-interações < 200ms.

---

## 12. Tendências 2026 → Receitas Prontas

Receitas diretas das tendências validadas em 2026. Aplique com intenção, não todas de uma vez.

### 12.1 Dark-Dominant (padrão para SaaS/AI)
- 60%+ das landings novas usam dark-dominant.
- Fundo `#0a0b0c`–`#121317`, texto off-white `#f4f4f5`, bordas de baixa opacidade (`rgba(255,255,255,0.08)`).
- Um único acento saturado (ex: electric blue) para CTAs e destaques.
- **Sempre com toggle light/dark funcional** (class + localStorage + system).

### 12.2 Bento Grid (o layout padrão de features)
- Grid assimétrico estilo widgets de macOS: células de tamanhos diferentes.
- `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6`, com células `lg:col-span-2`, `lg:col-span-4`.
- Uso principal: seção de features/métricas em SaaS.

### 12.3 Glassmorphism com Restrição
- `backdrop-blur` + fundo translúcido em **superfícies específicas** (nav overlay, cards) — não o site inteiro.
- Funciona melhor sobre dark com gradientes vibrantes de fundo.
- Aplicar de forma contida (não é mais a "linguagem visual" do site).

### 12.4 Tipografia Cinética
- 1 headline animada no hero (palavras que ciclam/morph/split) — NÃO repetir em toda página.
- CSS scroll-driven animations ou Framer Motion `AnimatePresence`.
- É "mais polimento que substância" — use como abertura forte.

### 12.5 Scrollytelling
- Conteúdo revelado conforme o scroll = narrativa guiada.
- Reage ao scroll **sem roubar o controle** (nada de scroll-jacking).
- CSS `animation-timeline: scroll()` nativo (sem JS) quando suportado.

### 12.6 Grão & Textura Tátil (antídoto ao "parece AI")
- CSS noise/grain overlay (`filter: url(#noise)`) ou imagem de grão em baixa opacidade.
- Textura em hero/headlines (stone, fabric, chrome) substitui gradiente text plano.
- Transmite "feito por humano".

### 12.7 Hero 3D (R3F / Spline)
- 1 objeto 3D central com material claro (glass, metal, stone), iluminação deliberada, fundo mínimo.
- Lazy-load (import dinâmico) — hero 3D pesado que atrasa LCP é negativo líquido.
- Fallback estático + `prefers-reduced-motion`.

### 12.8 Acentos Saturados Únicos
- Acentos `electric blue`, `burnt orange`, `lime`, `saturated pink` substituem pastéis 2022-23.
- Gradientes como **ferramenta cirúrgica**: 1 hero blob OU 1 CTA, não em todo fundo.

### 12.9 Barely-There UI (anti-design)
- Restrição máxima: 1 typeface, hairline borders de baixa opacidade, estrutura via whitespace/weight, não por boxes/sombras.

### 12.10 Anti-Grid Brutalism (nichos)
- Layouts "quebrados", monospace, `border-radius: 0`, pixels 1px, grão.
- Para dev-tools, estúdios criativos, marcas que querem sinalizar autenticidade.

---

## 13. Landing Pages & Conversão

Estrutura de landing de alta conversão (validada em 2026 — mobile-first, single-column narrative).

### 13.1 Anatomia (ordem de persuasão)
1. **Nav** — logo + 3-4 links + CTA (sticky, blur ao rolar).
2. **Hero** — headline 64–96px (outcome-focada) + subhead + 1 CTA + prova social (logos).
3. **Social proof** — logos de clientes / métricas.
4. **Problem/Agitate** — por que o status quo dói.
5. **Solution / Features** — bento grid.
6. **Product demo** — vídeo/gif interativo (não screenshot estático para SaaS).
7. **How it works** — 3 passos.
8. **Comparison table** — "vs concorrência" (maior conversor não-hero).
9. **Testimonials** — com foto + resultado mensurável.
10. **Pricing** — transparente, 3 tiers, tier destaque.
11. **FAQ** — accordion.
12. **Final CTA** + footer.

### 13.2 Regras de conversão
- **1 objetivo por página** — todo elemento constrói desejo, credibilidade OU reduz atrito.
- **Mobile-first, single-column** — o fluxo linear em 1 coluna vence multi-coluna no mobile.
- **CTAs acima da dobra + repetidos** — header, meio, final.
- **Trust signals perto de friction points** — selo/garantia ao lado do botão e do form.
- **Forms curtos** — quanto menos campos, mais conversão.
- **Headlines de outcome** — "Aumente X em Y", não "Nossa plataforma".
- **Contraste de CTA** — o botão principal é o elemento mais saturado da tela.

### 13.3 Micro-interações que convertem
- CTA que pulsa suavemente ao entrar no viewport.
- Contadores que animam ao scroll (stats).
- Progress bar de scroll.
- Before/after slider, calculadora de ROI.

---

## 14. Checklist de Qualidade Visual (Design Gate)

Gate automático de review visual. Rodar SEMPRE após implementar/editar uma UI.

### 14.1 Hierarquia & Layout
- [ ] 1 mensagem clara por seção
- [ ] Escala tipográfica consistente (tokens)
- [ ] Whitespace generoso e ritmo consistente
- [ ] Grid/alignment consistente (sem elementos soltos)

### 14.2 Cor & Contraste
- [ ] Texto ≥ 4.5:1 (normal) / 3:1 (grande)
- [ ] Cor nunca é o único sinal de estado
- [ ] 1 acento dominante (sem arco-íris)

### 14.3 Temas
- [ ] Light e dark funcionais (toggle + localStorage + system)
- [ ] Mesmas proporções de contraste nos 2 temas

### 14.4 Responsivo & Mobile
- [ ] Mobile-first testado (≥ 320px)
- [ ] Touch targets ≥ 44x44px
- [ ] Single-column no mobile, sem overflow horizontal

### 14.5 Motion & Performance
- [ ] Anima só transform/opacity
- [ ] ≤ 2 reveals por scroll
- [ ] `prefers-reduced-motion` respeitado
- [ ] LCP < 2.5s, CLS < 0.1 (assets lazy, fonts optimizada)

### 14.6 Acessibilidade
- [ ] Navegação por teclado completa
- [ ] ARIA correto (menus, diálogos, tabs)
- [ ] Skip link presente
- [ ] Focus visible em todo interativo

### 14.7 Verificação final
- [ ] Sem estética "genérica de AI" (ver checklist frontend-design no gui-super-expert)
- [ ] Direção estética BOLD e consistente
- [ ] Tipografia com personalidade (não só Inter default)

---

## 15. Matriz de Especialistas Complementares

Quando o design precisa de competência além da skill, **delegar/consultar**:

| Necessidade | Especialista/Skill | Como consultar |
|---|---|---|
| Layout web complexo (grids, sidebars, forms, dashboards) | `gui-layout-specialist` (L2) | Delegar task de layout |
| Mobile / Flutter / React Native | `mobile-ui-specialist` (L2) | Delegar task mobile |
| Arquitetura de software do app (SOLID, DDD, patterns) | `architect-design-specialist` (L2) | Design de estrutura front |
| Geração de imagens/assets on-demand | skill `image-gen` | Assets hero/backgrounds |
| Vídeo, 3D, Remotion, WebGL heroes | skill `remotion-best-practices` | Heroes 3D, motion video |
| TypeScript/React estrito | skill `typescript-patterns` | Código TS/TSX |
| Validação/qualidade do código | `reviewer` (core) | Review + Design Gate |
| Análise/exploração de estrutura | `analyzer` (core) | Antes de implementar |
| Documentação/changelog da mudança | `documenter` (core) | Docs + CHANGELOG |

**Fluxo recomendado para tarefa de UI:** `analyzer` (entender) → skill `ui-ux-system` (design) → L2/especialista se preciso → `coder` (implementar) → `reviewer` (Design Gate + code review).

---

## 16. Matriz de Repos Complementares

Repos recomendados (2026) — selecionar por caso de uso:

### Componentes & Design Systems
| Repo | Uso | Quando usar |
|---|---|---|
| `shadcn-ui/ui` | Copy-paste components, Radix-based, você é dono do código | Fundação de qualquer app React/Tailwind |
| `heroui-inc/heroui` (NextUI) | UI moderna e completa (v3) | Precisa de lib completa com Figma kit |
| `mantinedev/mantine` | 120+ componentes, 100+ hooks | Precisar de date pickers, spotlight, drag-drop prontos |
| `mui/base-ui` | Headless primitives (sucessor rápido do Radix) | Primitives sem estilo, atualização ativa |
| `cloudflare/kumo` | Componentes acessíveis (Base UI) da Cloudflare | Stack acessível moderno + docs CLI |
| `mui/material-ui` | Material Design completo | Apps enterprise estilo Google |
| `ant-design/ant-design` | Enterprise UI + design language | Dashboards corporativos, i18n |

### Efeitos & Animações
| Repo | Uso | Quando usar |
|---|---|---|
| `magicuidesign/magicui` | Animated components (shimmer, bento, particles) | Landing pages e marketing |
| `framer/motion` (ou `motion`) | Layout/scroll/gestures/transitions | Animações React em geral |
| `pmndrs/react-three-fiber` | 3D/WebGL em React | Hero 3D, visualização 3D |

### Dashboards & Dados
| Repo | Uso | Quando usar |
|---|---|---|
| `tremorlabs/tremor` | Dashboard components (charts, KPIs, sparklines) | Dashboards rápidos |
| `tremorlabs/tremor-raw` | Dashboard primitives headless | Dashboard sem opinião de estilo |
| `xyflow/xyflow` | Node-based flow editors | Workflow builders |

### Editores & Canvas
| Repo | Uso | Quando usar |
|---|---|---|
| `tldraw/tldraw` | Infinite canvas/whiteboard | Whiteboards colaborativos |
| `novel-bms/novel` | Editor rich text block-based | Editores tipo Notion |

### Recursos de Design
| Repo | Uso | Quando usar |
|---|---|---|
| `bradtraversy/design-resources-for-developers` | Curadoria mantida (fotos, mockups, cores, ícones) | Precisa de asset/recurso |
| `hqasmei/awesome-design-resources` | Recursos modernos (Tailwind, AI editors) | Referência atual de tooling |

### Ícones
| Repo | Uso | Quando usar |
|---|---|---|
| `lucide-icons/lucide` | Ícones 24x24 stroke, tree-shakable | Padrão primário |
| `tabler/tabler-icons` | 5000+ ícones SVG stroke | Cobertura extra |

### Templates SaaS
| Repo | Uso | Quando usar |
|---|---|---|
| `vercel/commerce` | E-commerce boilerplate Next.js | Lojas online |
| `saasfly/saasfly` | Full-stack SaaS (auth, billing, i18n) | Scaffold de SaaS |

---

## Design Hub — Fluxo de Decisão

```
Tarefa de UI/site/landing
   │
   ▼
1. Entender objetivo (converter? dashboard? portfólio?)
   │
   ▼
2. Escolher direção estética (minimal, dark-tech, vibrante, premium, brutalist...)
   │
   ▼
3. Definir tokens (cor, tipografia, espaço, radius, motion)
   │
   ▼
4. Montar estrutura (landing: anatomia seção 13 | app: grid/layout)
   │
   ▼
5. Aplicar tendência(s) com moderação (seção 12)
   │
   ▼
6. Implementar com repos certos (seção 16) + especialistas se preciso (seção 15)
   │
   ▼
7. Rodar Design Gate (seção 14) — fixar até passar
```

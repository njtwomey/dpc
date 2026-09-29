import type { ReactNode } from "react"
import { href } from "@/lib/base"
import { Button } from "@/components/ui/button"
import { Award, Images, Moon, Sun, Trophy, Users } from "lucide-react"

const NAV = [
  { path: "/awarders/", label: "Awarders", icon: Award },
  { path: "/challenges/", label: "Challenges", icon: Trophy },
  { path: "/recipients/", label: "Recipients", icon: Users },
]

/** The shell every page shares. Plain <a> links, so each page stands alone as
 *  static HTML and deep links work without any JavaScript. */
export function Layout({ active, children }: { active?: string; children: ReactNode }) {
  return (
    <div className="bg-background min-h-screen">
      <header className="bg-background/80 sticky top-0 z-40 border-b backdrop-blur">
        <div className="mx-auto flex h-14 max-w-7xl items-center gap-1 px-4">
          <a href={href("/")} className="mr-3 flex items-center gap-2 text-sm font-semibold">
            <Images className="size-4" /> DPChallenge Awards
          </a>
          {NAV.map(({ path, label, icon: Icon }) => (
            <a
              key={path}
              href={href(path)}
              data-active={active === label ? "" : undefined}
              className="hover:bg-accent data-[active]:bg-secondary inline-flex h-8 items-center gap-1.5 rounded-md px-3 text-sm font-medium transition-colors"
            >
              <Icon className="size-4" /> {label}
            </a>
          ))}
          {/* A Button, not shadcn's Toggle: Toggle keeps `pressed` in React
              state and nothing in this header is ever mounted. Which icon
              shows is already decided by the `dark` class on <html>, so the
              markup is identical on all 3,000 prerendered pages and
              client.tsx only has to flip the class. */}
          <Button
            variant="ghost"
            size="icon-sm"
            data-theme-toggle=""
            aria-label="Switch between light and dark"
            className="scripted:inline-flex ml-auto hidden"
          >
            <Sun className="size-4 dark:hidden" />
            <Moon className="hidden size-4 dark:block" />
          </Button>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-8">{children}</main>
      <footer className="text-muted-foreground mt-16 border-t py-8 text-center text-xs">
        <p>All photographs are owned by the photographer.</p>
      </footer>
    </div>
  )
}

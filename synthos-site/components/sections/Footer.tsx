import GradientText from "@/components/ui/GradientText";

export default function Footer() {
  return (
    <footer className="relative z-10 border-t border-void-border py-12 px-6">
      <div className="max-w-5xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
        <div>
          <div className="text-xl font-bold font-mono">
            <GradientText>SYNTHOS</GradientText>
          </div>
          <p className="text-text-muted text-sm mt-1">
            Synthesize stories. Ship scenes. Scale everything.
          </p>
        </div>

        <div className="flex items-center gap-8 text-sm text-text-muted">
          <a href="#waitlist-cta" className="hover:text-text-primary transition-colors">
            Join Waitlist
          </a>
          <span>
            &copy; {new Date().getFullYear()} SYNTHOS. All rights reserved.
          </span>
        </div>
      </div>
    </footer>
  );
}

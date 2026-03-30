import { useState } from "react";
import { cn } from "@/lib/utils";

const Navbar = () => {
  const [activeTab, setActiveTab] = useState<"login" | "signup">("signup");

  return (
    <nav className="fixed top-0 flex w-full items-center justify-between bg-black/10 px-4 py-4 backdrop-blur-[16px] border-b border-white/10 md:px-8 z-50">
      <div className="flex items-center gap-2 cursor-pointer">
        {/* Branding removed per request */}
      </div>

      <div className="flex items-center gap-1">
        <button 
          onClick={() => setActiveTab("login")}
          className={cn(
             "font-[500] rounded-xl tracking-tight h-9 px-5 transition-all duration-300",
             activeTab === "login" 
               ? "bg-zinc-900/90 text-white border border-white/5" 
               : "text-white/70 hover:text-white bg-transparent border border-transparent"
          )}
        >
          Log in
        </button>
        <button 
          onClick={() => setActiveTab("signup")}
          className={cn(
             "font-[500] rounded-xl tracking-tight h-9 px-5 transition-all duration-300",
             activeTab === "signup" 
               ? "bg-zinc-900/90 text-white border border-white/5" 
               : "text-white/70 hover:text-white bg-transparent border border-transparent"
          )}
        >
          Sign up
        </button>
      </div>
    </nav>
  );
};

export default Navbar;

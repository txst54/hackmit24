import {Spotlight} from "@/components/ui/spotlight";
import {Button} from "@/components/ui/button";
import Link from "next/link";

export default function Home() {
  const border_b = "border-b border-dashed border-zinc-700 ";
  const border_r = "border-r border-dashed border-zinc-700 ";
  const border_l = "border-l border-dashed border-zinc-700 ";
  const border_t = "border-t border-dashed border-zinc-700 ";
  return (
      <div className="bg-black">
        {/* Splash Screen */}
        <div className="min-h-screen flex flex-col bg-black/[0.96] antialiased">
          <Spotlight
              className="-top-40 left-0 md:left-60 md:-top-20"
              fill="white"
          />
          <div className="flex-1 flex items-center justify-center">
            {/* Overlay Content */}
            <div className={`text-center z-10 px-8`}>
              <p className={`text-white text-4xl sm:text-8xl py-8 p-8 rounded-3xl ${border_b + border_l + border_r}`}>Cherubim</p>
              <div className={`max-w-6xl flex flex-row justify-center mt-4 px-2 py-8 rounded-3xl ${border_t + border_l + border_r}`}>
                <p
                    className={`bg-clip-text text-transparent bg-gradient-to-b from-neutral-200 to-neutral-500 text-base sm:text-2xl font-light`}>
                  Partnering with elite companies, TCC{' '}
                  <b className={`text-white`}>
                    accelerates financial research
                  </b>{' '}
                  through algorithmic trading and comprehensive valuation
                </p>
              </div>
              <Link href="/login" className="loginButton border-white border text-white hover:bg-white hover:text-black text-xl rounded-xl px-6 py-2 mt-4">Sign in</Link>
            </div>
          </div>
        </div>
      </div>
  );
}

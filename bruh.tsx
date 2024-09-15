import {Spotlight} from "@/components/ui/spotlight";
import Link from "next/link";

interface Project {
    name: string,
    image?: string,
    description: string
}

export default function LandingPage() {
    // const [isLightMode, setIsLightMode] = useState('dark');
    const isLightMode = 'dark';
    const projects: Project[] = [
        {
            name: "Peachtree Group",
            description: "Automating creation of asset management models for Peachtree Group's deals exceeding $50mm. ",
            image: "/assets/projects/logos/peachtree.jpg",
        },
        {
            name: "TradeChoice",
            image: "/assets/projects/logos/tradechoice.webp",
            description: "Engineering technical analysis indicators and a full-stack dashboard for TradeChoice LLC."
        },
        {
            name: "WXLLSPACE",
            image: "/assets/projects/logos/wxllspace_logo.png",
            description: "Pioneering a LLM-powered art-style recommendation system for WXLLSPACE's full-stack platform."
        },
        {
            name: "TCC Platform",
            description: "Built up a comprehensive full-stack membership management automation platform for TCC."
        },
        {
            name: "TCC Back-tester",
            description: "Designed our in-house back-testing engine for algorithmic trading and charting."
        },
        {
            name: "TCC Algo Suite",
            description: "Compiled together a diverse array of trading algorithms from Double-EMA to Delta Hedging."
        }
    ];

    /*
    @TODO add in light mode
    useEffect(() => {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: light)');
      const handleChange = () => setIsLightMode(mediaQuery.matches);

      mediaQuery.addEventListener('change', handleChange);

      return () => mediaQuery.removeEventListener('change', handleChange);
    }, []);
    */

    const getImageForProject = (projectName: string) => {
        if (projectName === 'TradeChoice') {
            return isLightMode ? "/assets/projects/logos/tradechoice.webp" : "/assets/projects/logos/tradechoice_dark.jpg";
        }
        return projectName;
    };

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
                    <img src={"/assets/banner_official.png"} className="absolute w-full h-full object-cover grayscale opacity-20" alt="Texas Capital Collective Banner" />
                    {/* Overlay Content */}
                    <div className={`text-center z-10 px-8`}>
                        <p className={`text-white text-4xl sm:text-8xl py-8 p-8 rounded-3xl ${border_b + border_l + border_r}`}>Texas Capital Collective</p>
                        <div className={`max-w-6xl flex flex-row justify-center mt-4 px-2 py-8 rounded-3xl ${border_t + border_l + border_r}`}>
                            <p
                                className={`bg-clip-text text-transparent bg-gradient-to-b from-neutral-200 to-neutral-500 text-lg sm:text-2xl font-light`}>
                                Partnering with elite companies, TCC{' '}
                                <b className={`text-white`}>
                                    accelerates financial research
                                </b>{' '}
                                through algorithmic trading and comprehensive valuation
                            </p>
                        </div>
                        {/*<Link href="/login" className="loginButton border-white border text-white text-xl rounded-xl px-6 py-2 mt-4">Join</Link>*/}
                    </div>
                </div>
            </div>

            {/* Our Projects */}
            <div className="flex justify-center border-y border-zinc-700">
                <div className="md:w-9/12 2xl:w-7/12 w-5/6 p-4 lg:p-16">
                    <div className="text-white md:pb-8 pb-2">
                        <h2 className="text-2xl md:text-4xl font-semibold">Ambition when it matters</h2>
                        <p className="text-2xl md:text-4xl text-zinc-400">We produce large-scale solutions</p>
                    </div>
                    <div className="pt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {projects.map((project, index) => (
                            <div key={index} className="border border-zinc-700 rounded-2xl hover:border-zinc-500 hover:bg-gradient-to-b transition-all duration-200 from-zinc-900 to-black overflow-hidden space-y-4 p-4">
                                {project.image && (<img src={project.name === "TradeChoice" ? getImageForProject(project.name) : project.image} className={"rounded-full w-24 h-24 object-cover mx-auto border-zinc-700 border"} alt={project.name} />)}
                                <div className="text-white text-xl font-semibold w-full text-center">{project.name}</div>
                                <div className="w-full text-zinc-500 text-center">{project.description}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Join Us */}
            <div className="flex flex-col md:flex-row justify-center items-center mx-auto">
                <div className="flex flex-col md:flex-row w-5/6 md:w-9/12 2xl:w-7/12 border-l border-zinc-700 border-dashed">
                    <div className="w-full md:w-7/12 px-4 md:px-12 py-8 md:pt-16 md:pb-8 text-white border-b md:border-b-0 md:border-zinc-700 border-dashed">
                        <h1 className="text-2xl md:text-3xl lg:text-4xl font-semibold">Driven Membership</h1>
                        <h2 className="text-2xl text-zinc-400 mt-2 md:mt-4">Undergrad at UT? Join Us!</h2>
                        <p className="text-zinc-500 mt-8">
                            We assemble the brightest and most ambitious students to create beautiful solutions.
                        </p>
                        <p className="text-white text-2xl mt-8">
                            {`There\'s no application.`}
                        </p>
                        <p className="text-zinc-500 mt-2">
                            Instead of an application, we ask you contribute to one of our open-source projects listed above to be listed as a developer. Analysts and developers will be assigned to our <b className="text-zinc-300">corporate projects</b> and receive direct access to our <b className="text-zinc-300">portfolio fund</b>.
                        </p>
                        <p className="text-white text-2xl mt-8">
                            Just want to learn?
                        </p>
                        <p className="text-zinc-500 mt-2 mb-8">
                            We host analyst groups for IB and Quantitative Finance weekly. Register as a member to attend.
                        </p>
                    </div>
                    <div className="flex justify-center items-center w-full md:w-5/12 p-8 ">
                        <img src={"/assets/pge.jpg"} alt="Membership visual" className="max-w-full h-auto rounded-2xl border border-zinc-500" />
                    </div>
                </div>
            </div>
        </div>
    );
}
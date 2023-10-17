import { useContext, useEffect } from "react";
import { FaCog, FaFilePdf, FaGithub } from "react-icons/fa";
import {
  BrowserRouter,
  Link,
  Navigate,
  useLocation,
  useRoutes,
} from "react-router-dom";

import { PrecomputedParams } from "./components/Precomputed";
import { RedditURLParams } from "./components/RedditURL";
import { StoredParams } from "./components/Stored";
import { Toggle } from "./components/Toggle";
import { Tooltip } from "./components/Tooltip";
import { PrecomputedListProvider } from "./context/precomputed_list";
import { SettingsContext, SettingsProvider } from "./context/settings";

const ScrollRouterTop = ({ children }) => {
  const location = useLocation();
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [location]);

  return children;
};

function Router({ children }) {
  return (
    <BrowserRouter>
      <ScrollRouterTop>{children}</ScrollRouterTop>
    </BrowserRouter>
  );
}

const routes = [
  {
    path: "/precomputed",
    name: "Precomputed Examples",
    element: <PrecomputedParams />,
  },
  { path: "/stored", element: <StoredParams /> },
  {
    path: "/from_url",
    name: "New Discussion",
    element: <RedditURLParams />,
  },
  { path: "*", element: <Navigate to="/precomputed" replace /> },
];

function Content() {
  return useRoutes(routes);
}

function SettingsTooltip({ children, ...probs }) {
  return (
    <Tooltip {...probs} tooltip={children}>
      <FaCog size={18} className="text-slate-200 hover:text-slate-400" />
    </Tooltip>
  );
}

function Navbar() {
  const {
    visualizeClusters,
    setVisualizeClusters,
    coloredText,
    setColoredText,
    showMinimap,
    setShowMinimap,
  } = useContext(SettingsContext);
  const { pathname } = useLocation();
  return (
    <div className="flex flex-wrap items-center justify-between gap-x-6 gap-y-1 border-b-2 border-black bg-gray-800 p-4 px-4 text-neutral-100 md:flex-nowrap">
      <div
        href="/"
        target="_blank"
        title="Indicative Summarization of Long Discussions"
        className="min-w-0 overflow-hidden overflow-ellipsis font-bold lg:whitespace-nowrap"
      >
        Indicative Summarization of Long Discussions
      </div>
      <div className="flex flex-wrap gap-x-4 gap-y-1 sm:flex-nowrap">
        {routes
          .filter(({ name }) => name !== undefined)
          .map(({ path, name }) => (
            <Link
              key={path}
              to={path}
              className={`${
                pathname === path
                  ? "text-[#ff4500] underline underline-offset-2"
                  : "text-gray-300 hover:text-gray-400"
              } whitespace-nowrap`}
            >
              {name}
            </Link>
          ))}
      </div>
      <div className="flex items-center gap-6">
        <SettingsTooltip place="bottom" clickable>
          <div className="flex flex-col justify-center gap-x-6 gap-y-2 lg:flex-nowrap">
            <div className="flex items-center gap-2">
              <div className="flex grow justify-between gap-2">
                <span
                  className="whitespace-nowrap"
                  title="When enabled, sentence that are part of a cluster are highlighted with the color of the cluster using the same color as background."
                >
                  Colored Text
                </span>
                <Toggle checked={coloredText} onChange={setColoredText} />
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="flex grow justify-between gap-2">
                <span
                  className="whitespace-nowrap"
                  title="When enabled, a plot will be shown at the bottom of the thread in the frame view."
                >
                  Visualize Clusters
                </span>
                <Toggle
                  checked={visualizeClusters}
                  onChange={setVisualizeClusters}
                />
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="flex grow justify-between gap-2">
                <span
                  className="whitespace-nowrap"
                  title="When enabled, a minimap will be shown to the right of the thread in the frame view."
                >
                  Toggle Minimap
                </span>
                <Toggle checked={showMinimap} onChange={setShowMinimap} />
              </div>
            </div>
          </div>
        </SettingsTooltip>
        <div className="flex items-center gap-3">
          <div>
            <a
              className="underline decoration-transparent transition duration-100 ease-in-out hover:text-blue-500 hover:decoration-inherit"
              href="https://github.com/webis-de/emnlp23-indicative-summarization-of-long-discussions"
              target="_blank"
              rel="noreferrer"
            >
              <FaGithub />
            </a>
          </div>
          <div>
            <FaFilePdf />
          </div>
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <SettingsProvider>
      <PrecomputedListProvider>
        <Router>
          <div className="flex h-screen flex-col overflow-hidden">
            <Navbar />
            <Content />
          </div>
        </Router>
      </PrecomputedListProvider>
    </SettingsProvider>
  );
}

export default App;

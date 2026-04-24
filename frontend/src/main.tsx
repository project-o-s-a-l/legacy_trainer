import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import "./app/styles/index.ts";
import { App } from "@/app/index";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "./features/AutchContext/AuthContext.tsx";

createRoot(document.getElementById("root")!).render(
	<StrictMode>
		<BrowserRouter>
			<AuthProvider>
				<App />
			</AuthProvider>
		</BrowserRouter>
	</StrictMode>,
);

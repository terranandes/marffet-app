"use client";

import PageTransition from "../components/PageTransition";

export default function RootTemplate({ children }: { children: React.ReactNode }) {
    // template.tsx creates a new instance on every navigation,
    // making it ideal for standard enter animations in the App Router.
    return <PageTransition>{children}</PageTransition>;
}

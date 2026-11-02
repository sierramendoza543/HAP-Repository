import { permanentRedirect } from "next/navigation";

// The district-level scores now live on the dashboard and on each town's page.
export default function V2Page() {
  permanentRedirect("/");
}

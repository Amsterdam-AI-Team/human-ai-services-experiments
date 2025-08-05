import { browser } from "$app/environment";
import { goto } from "$app/navigation";
import { clearApiResponses } from "$lib/stores/apiStore";
import { setLanguage } from "$lib/stores/languageStore";

const INACTIVITY_TIMEOUT = 2 * 60 * 1000; // 2 minutes in milliseconds

export class InactivityTimer {
  private timer: number | null = null;
  private resetPath: string;
  private events = [
    "mousedown",
    "mousemove",
    "keypress",
    "scroll",
    "touchstart",
    "click",
  ];

  constructor(resetPath: string) {
    this.resetPath = resetPath;
    this.resetTimer = this.resetTimer.bind(this);
    this.handleInactivity = this.handleInactivity.bind(this);
  }

  start() {
    if (!browser) return;

    this.resetTimer();
    this.events.forEach((event) => {
      document.addEventListener(event, this.resetTimer, true);
    });
  }

  stop() {
    if (!browser) return;

    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }

    this.events.forEach((event) => {
      document.removeEventListener(event, this.resetTimer, true);
    });
  }

  private resetTimer() {
    if (this.timer) {
      clearTimeout(this.timer);
    }

    this.timer = setTimeout(
      this.handleInactivity,
      INACTIVITY_TIMEOUT,
    ) as unknown as number;
  }

  private handleInactivity() {
    // Clear all API store data
    clearApiResponses();
    setLanguage('nl');

    // Redirect to the appropriate concept root
    goto(this.resetPath);
  }
}

// Utility function to create and start timer for concept routes
export function startInactivityTimer(currentPath: string) {
  if (!browser) return null;

  let resetPath: string;
  if (currentPath.startsWith("/1")) {
    resetPath = "/1";
  } else if (currentPath.startsWith("/2")) {
    resetPath = "/2";
  } else {
    return null; // Not a concept route
  }

  const timer = new InactivityTimer(resetPath);
  timer.start();
  return timer;
}

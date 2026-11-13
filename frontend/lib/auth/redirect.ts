/**
 * Accepts only a same-site path, so `?redirectTo=` can't send a user to another
 * site after signing in. Rejects `//host` (protocol-relative), backslashes
 * (browsers treat `\` as `/`) and control characters (browsers strip tabs and
 * newlines, so `/<TAB>/host` would become `//host`).
 */
export function safeRedirect(target: unknown, fallback = "/") {
  if (typeof target !== "string") return fallback
  if (!target.startsWith("/") || target.startsWith("//")) return fallback
  if (target.includes("\\") || /[\u0000-\u001f\u007f]/.test(target)) {
    return fallback
  }
  return target
}

import { NextResponse, type NextRequest } from "next/server";

/**
 * Portão de UX: redireciona apenas quando não há sessão alguma. O access
 * expira em 15 min, mas o refresh dura 30 dias — se só o refresh estiver
 * presente, a página entra e o `apiFetch` renova o access no primeiro 401.
 * A autoridade real é o FastAPI: `/me` valida o JWT e as rotas validam papéis.
 */
export function middleware(request: NextRequest) {
  if (!request.cookies.has("tt_access") && !request.cookies.has("tt_refresh")) {
    const url = new URL("/login", request.url);
    url.searchParams.set("next", request.nextUrl.pathname);
    return NextResponse.redirect(url);
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/app/:path*", "/onboarding", "/providers"],
};

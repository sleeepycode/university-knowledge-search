import { NavLink } from "react-router-dom";
import type { ReactNode } from "react";

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="app">
      <header className="header">
        <div className="container header__inner">
          <NavLink to="/" className="logo">
            DocSearch
          </NavLink>
          <nav className="nav">
            <NavLink to="/" className={({ isActive }) => (isActive ? "nav__link active" : "nav__link")}>
              Загрузка
            </NavLink>
            <NavLink
              to="/search"
              className={({ isActive }) => (isActive ? "nav__link active" : "nav__link")}
            >
              Поиск
            </NavLink>
          </nav>
        </div>
      </header>
      <main className="main container">{children}</main>
    </div>
  );
}

import { Link } from "react-router-dom";

function Navbar() {
  const token = localStorage.getItem("token");

  const user = JSON.parse(
    localStorage.getItem("user")
  );

  const cart =
    JSON.parse(localStorage.getItem("cart")) || [];

  const logoutHandler = () => {
    localStorage.removeItem("token");

    localStorage.removeItem("user");

    window.location.href = "/login";
  };

  return (
    <nav className="bg-white shadow-lg px-10 py-5 flex justify-between items-center sticky top-0 z-50">
      <Link to="/">
        <h1 className="text-3xl font-extrabold text-black">
          AI Shop
        </h1>
      </Link>

      <div className="hidden md:flex gap-8 text-lg font-medium">
        <Link to="/">Home</Link>

        <Link to="/products">
          Products
        </Link>

        <Link to="/admin">Admin</Link>
      </div>

      <div className="flex items-center gap-6">
        <Link
          to="/cart"
          className="relative text-2xl"
        >
          🛒

          <span className="absolute -top-2 -right-3 bg-red-500 text-white text-xs px-2 py-1 rounded-full">
            {cart.length}
          </span>
        </Link>

        {!token ? (
          <>
            <Link to="/login">
              Login
            </Link>

            <Link
              to="/register"
              className="bg-black text-white px-5 py-2 rounded-xl"
            >
              Register
            </Link>
          </>
        ) : (
          <>
            <span className="font-semibold">
              Hello, {user?.name}
            </span>

            <button
              onClick={logoutHandler}
              className="bg-red-500 text-white px-5 py-2 rounded-xl"
            >
              Logout
            </button>
          </>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
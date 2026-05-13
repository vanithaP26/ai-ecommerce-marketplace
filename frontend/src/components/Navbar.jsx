import { Link } from "react-router-dom";

function Navbar() {
  const token = localStorage.getItem("token");

  const user = JSON.parse(
    localStorage.getItem("user")
  );

  const logoutHandler = () => {
    localStorage.removeItem("token");

    localStorage.removeItem("user");

    window.location.href = "/login";
  };

  return (
    <nav className="bg-black text-white px-8 py-4 flex justify-between items-center">
      <h1 className="text-2xl font-bold">
        AI Shop
      </h1>

      <div className="flex gap-6 items-center">
        <Link to="/">Home</Link>

        <Link to="/products">
          Products
        </Link>

        <Link to="/cart">Cart</Link>

        {!token ? (
          <>
            <Link to="/login">Login</Link>

            <Link to="/register">
              Register
            </Link>
          </>
        ) : (
          <>
            <span>
              Hello, {user?.name}
            </span>

            <button
              onClick={logoutHandler}
              className="bg-red-500 px-4 py-2 rounded-lg"
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
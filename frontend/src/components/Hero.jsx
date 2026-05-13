function Hero() {
  return (
    <section className="bg-gray-100 min-h-[80vh] flex items-center justify-center px-6">
      <div className="text-center max-w-3xl">
        <h1 className="text-6xl font-bold text-gray-900 leading-tight">
          AI Powered Ecommerce Marketplace
        </h1>

        <p className="mt-6 text-xl text-gray-600">
          Smart shopping experience with AI recommendations,
          analytics, and optimized performance.
        </p>

        <button className="mt-8 bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg text-lg font-semibold transition">
          Shop Now
        </button>
      </div>
    </section>
  );
}

export default Hero;
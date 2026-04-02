import ScrollVideo from "@/components/ScrollVideo";
import Navbar from "@/components/Navbar";

const Index = () => {
  return (
    <div className="bg-background text-foreground relative">
      <Navbar />
      {/* Lazy load ScrollVideo */}
      <ScrollVideo />
    </div>
  );
};

export default Index;

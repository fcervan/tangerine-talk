import RegisterForm from "@/components/RegisterForm";
import LocaleSwitcher from "@/components/LocaleSwitcher";

export default function CadastroPage() {
  return (
    <main className="flex min-h-screen flex-col bg-mist">
      <div className="flex justify-end px-5 py-5 sm:px-8">
        <LocaleSwitcher />
      </div>
      <div className="flex flex-1 items-center justify-center px-5 pb-16">
        <RegisterForm />
      </div>
    </main>
  );
}
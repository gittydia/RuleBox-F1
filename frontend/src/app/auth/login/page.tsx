import AuthForm from "../../../../components/AuthForm";

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0d0d0d]">
      <AuthForm type="login" />
    </div>
  );
}

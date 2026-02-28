export function getUserIdentifier() {
  return sessionStorage.getItem("student_email") || "guest";
}

public class test4 {
    public boolean checkAccess(String role, int clearLevel) {
        if (role.equals("ADMIN") || clearLevel > 10) {
            return true;
        }
        return false;
    }
}
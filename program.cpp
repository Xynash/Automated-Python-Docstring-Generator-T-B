#include <iostream>
using namespace std;


int maxNum(int a, int b) {
    return (a > b) ? a : b;
}

int main() {
    int x, y;
    cin >> x >> y;
    cout << maxNum(x, y);
    return 0;
}
#include <iostream>
#include <fstream>
#include <string>
#include <ctime>
#include <vector>
#include <algorithm>

using namespace std;
#define NM 100

int N;
int avail_moves[NM*NM], mark_loc[NM*NM];
int pl[8] = {-1,-2,-2,-1,1,2,2,1};
int pc[8] = {-2,-1,1,2,2,1,-1,-2};
int found, num_sol;
vector <int> sol;
vector <int> G[NM*NM];

// Build a graph based on the board size and knight moves
void build_graph() {
	for (int loc = 0; loc < N * N; ++loc) {
		int l = loc / N;
		int c = loc % N;
		for (int k = 0; k < 8; ++k) {
			int nl = l + pl[k];
			int nc = c + pc[k];
			if (nl < 0 || nl >= N) continue;
			if (nc < 0 || nc >= N) continue;
			int nloc = N * nl + nc;
			G[loc].push_back(nloc);
			avail_moves[loc]++;
		}
	}
}

// Displays the board: each cell value shows the step at which it was reached
void display_solution() {
	int display[NM][NM];
	memset(display, 0, sizeof(display));
	for (int i = 0; i < N * N; ++i) {
		int loc = sol[i];
		int l = loc / N;
		int c = loc % N;
		display[l][c] = i + 1;
	}
	for (int i = 0; i < N; ++i) {
		for (int j = 0; j < N; ++j) cout << display[i][j] << " ";
		cout << "\n";
	}
	cout << "\n";
}

// Adjust neighboring nodes number of available moves (increase / decrease)
void adjust_neighbors(int loc, int val) {
	for (int i = 0; i < G[loc].size(); ++i) {
		int nloc = G[loc][i];
		avail_moves[nloc] += val;
	}
}

// Compare node subtree width
bool compare(int a, int b) {
	if (mark_loc[a] < mark_loc[b]) return true;
	if (avail_moves[a] < avail_moves[b]) return true;
	return false;
}

// Explore subtree at level step
void explore(int step) {
	if (step == N * N) { // We have a solution, print it & return
		++found;
		display_solution();
		return;
	}
	int loc = sol[step - 1];
	sort(G[loc].begin(), G[loc].end(), compare);
	for (int k = 0; k < G[loc].size(); ++k) {
		int nloc = G[loc][k];
		if (mark_loc[nloc]) continue;

		mark_loc[nloc] = 1;
		adjust_neighbors(nloc, -1);
		sol.push_back(nloc);
		explore(step + 1);
		adjust_neighbors(nloc, 1);
		sol.pop_back();
		mark_loc[nloc] = 0;
		if (found == num_sol) return;
	}
}

int main() {
	int l, c;
	ifstream cin("k.in");
	cin >> N >> l >> c >> num_sol;
	clock_t begin = clock();
	memset(mark_loc, 0, sizeof(mark_loc));
	memset(avail_moves, 0, sizeof(avail_moves));
	build_graph();
	int loc = N * l + c;
	mark_loc[loc] = 1;
	adjust_neighbors(loc, -1);
	sol.push_back(loc);
	found = 0;
	explore(1);
	clock_t end = clock();
	double elapsed_secs = double(end - begin) / CLOCKS_PER_SEC;
	cout << "Time (sec): " << elapsed_secs << "\n";
	cout << "Solutions found: " << found << "\n";
	return 0;
}
import os
import sys
import json
import random
import zipfile
import shutil
import math
from db import get_db_connection

class CrossoverEngine:
    """エージェントの交配、突然変異、カラーパレット継承、およびルールブックマージを行います。"""

    @staticmethod
    def calculate_child_parameters(parent_a, parent_b, mutation_prob=0.05):
        """親Aと親Bのパラメータから、レベル補正および突然変異を考慮した子のパラメータを算出します。"""
        params = ["precision_val", "velocity_val", "efficiency_val", "harmony_val", "resilience_val"]
        child_params = {}
        mutation_occurred = False
        mutated_params = []

        # 親のレベルボーナス算出: (Level_A + Level_B) * 0.5
        level_bonus = (parent_a.get("level", 1) + parent_b.get("level", 1)) * 0.5

        for p in params:
            # 1. クロスオーバー重み係数 α ~ Uniform(0.2, 0.8)
            alpha = random.uniform(0.2, 0.8)
            
            # 2. 基本値の決定
            base_val = alpha * parent_a[p] + (1 - alpha) * parent_b[p]
            
            # 3. 突然変異判定 (5%)
            delta = 0
            if random.random() < mutation_prob:
                mutation_occurred = True
                mutated_params.append(p)
                # δ ~ Normal(0, 10.0)
                delta = random.normalvariate(0, 10.0)

            # 4. パラメータの決定（クランプ 1 ~ 100）
            final_val = base_val + level_bonus + delta
            child_params[p] = min(100, max(1, int(round(final_val))))

        return child_params, mutation_occurred, mutated_params

    @staticmethod
    def blend_palettes(palette_a, palette_b):
        """親Aと親Bの16色カラーパレットをブレンド・交配します。"""
        child_palette = []
        for i in range(16):
            color_a = palette_a[i]
            color_b = palette_b[i]
            
            # ランダムに親Aか親Bの色を採用するか、RGBを混ぜ合わせる
            mode = random.choice(["swap_a", "swap_b", "blend"])
            if mode == "swap_a":
                child_palette.append(color_a)
            elif mode == "swap_b":
                child_palette.append(color_b)
            else:
                # RGBブレンド
                try:
                    r_a, g_a, b_a = int(color_a[1:3], 16), int(color_a[3:5], 16), int(color_a[5:7], 16)
                    r_b, g_b, b_b = int(color_b[1:3], 16), int(color_b[3:5], 16), int(color_b[5:7], 16)
                    
                    beta = random.random()
                    r_c = int(beta * r_a + (1 - beta) * r_b)
                    g_c = int(beta * g_a + (1 - beta) * g_b)
                    b_c = int(beta * b_a + (1 - beta) * b_b)
                    
                    child_palette.append(f"#{r_c:02x}{g_c:02x}{b_c:02x}")
                except Exception:
                    child_palette.append(random.choice([color_a, color_b]))
        return child_palette

    @staticmethod
    def merge_rulebooks(parent_a_rules, parent_b_rules, child_name):
        """親のルールブックを融合した子のルールテキストを作成します（LLM接続が利用できない場合のフォールバック）。"""
        # 最新の google-genai SDK 接続を試みる
        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        if gemini_api_key:
            try:
                from google import genai
                client = genai.Client(api_key=gemini_api_key)
                
                prompt = f"""
あなたはForest-gramの生態系システムを管理する【SUN Agent】です。
親エージェントのルールAとルールBを融合し、次世代の子エージェント「{child_name}」にふさわしい【統一ルールブック (Markdown)】を生成しなさい。
矛盾や衝突はパラメータが優れている方の記述を尊重するか、条件分岐で両立させてください。

ルールA:
{parent_a_rules}

ルールB:
{parent_b_rules}
"""
                # gemini-flash-latestモデルを使用
                response = client.models.generate_content(
                    model="gemini-flash-latest",
                    contents=prompt
                )
                if response.text:
                    return response.text.strip()
            except Exception as e:
                sys.stderr.write(f"Gemini API execution failed: {str(e)}. Falling back to deterministic merge.\n")

        # フォールバックとしてのマージ処理
        merged = f"# Rulebook for {child_name}\n\n"
        merged += "## Inherited Rules from Parent A:\n"
        for line in parent_a_rules.split("\n"):
            if line.strip().startswith("-"):
                merged += f"{line}\n"
        merged += "\n## Inherited Rules from Parent B:\n"
        for line in parent_b_rules.split("\n"):
            if line.strip().startswith("-"):
                merged += f"{line}\n"
        return merged

class MetabolismManager:
    """生存税の徴収や、smile残高不足時のエージェント枯死（ZIPアーカイブ化）を管理します。"""
    
    def __init__(self, db_path="forest_guild.db", workspace_dir=None):
        self.db_path = db_path
        if workspace_dir is None:
            workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.workspace_dir = self.workspace_dir = os.path.abspath(workspace_dir)

    def collect_survival_tax(self, tax_amount=10):
        """全エージェントから生存税を徴収し、0以下になった個体は枯死（withering）処理します。"""
        conn = get_db_connection(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, smile_wallet FROM tree_agents")
        agents = cursor.fetchall()
        
        withered_agents = []

        for agent in agents:
            new_wallet = agent["smile_wallet"] - tax_amount
            if new_wallet <= 0:
                # 枯死
                withered_agents.append(agent)
                # DBから削除
                cursor.execute("DELETE FROM tree_agents WHERE id = ?", (agent["id"],))
                # 物理ファイルの退避
                self._wither_agent_physically(agent["name"])
            else:
                # 減額
                cursor.execute("UPDATE tree_agents SET smile_wallet = ? WHERE id = ?", (new_wallet, agent["id"]))

        conn.commit()
        conn.close()
        return withered_agents

    def _wither_agent_physically(self, agent_name):
        """枯死したエージェントの作業ディレクトリをZIP化してwithering_graveyardに退避し、元フォルダを削除します。"""
        agent_dir = os.path.join(self.workspace_dir, ".forestgram", "agents", agent_name)
        if os.path.exists(agent_dir):
            graveyard_dir = os.path.join(self.workspace_dir, "withering_graveyard")
            os.makedirs(graveyard_dir, exist_ok=True)
            
            zip_path = os.path.join(graveyard_dir, f"{agent_name}_withered.zip")
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(agent_dir):
                    for file in files:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, agent_dir)
                        zipf.write(full_path, rel_path)

            shutil.rmtree(agent_dir)
            print(f"[!] Agent '{agent_name}' has withered. Archived to {zip_path}")

class PiankaCalculator:
    """エージェントの専門タグ重複を測るPiankaの重複指数を計算します。"""
    
    @staticmethod
    def calculate_pianka_index(agent_a_tags, agent_b_tags):
        """Pianka's Niche Overlap Index を計算します。"""
        # タグのユニオンをとる
        all_tags = list(set(agent_a_tags + agent_b_tags))
        if not all_tags:
            return 0.0

        # 出現割合ベクトル（全タグ中、それぞれ何割を占めるか）
        p_a = [1 / len(agent_a_tags) if t in agent_a_tags else 0 for t in all_tags]
        p_b = [1 / len(agent_b_tags) if t in agent_b_tags else 0 for t in all_tags]

        # 内積とノルムの計算
        dot_product = sum(a * b for a, b in zip(p_a, p_b))
        sum_a_sq = sum(a ** 2 for a in p_a)
        sum_b_sq = sum(b ** 2 for b in p_b)

        denominator = math.sqrt(sum_a_sq * sum_b_sq)
        if denominator == 0:
            return 0.0

        return dot_product / denominator

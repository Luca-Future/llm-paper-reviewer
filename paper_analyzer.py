import os
import json
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Import PDF parser functionality
try:
    from pdf_parser import pdf_to_markdown
except ImportError:
    print("Warning: pdf_parser.py not found. PDF support disabled.")
    pdf_to_markdown = None


# Load environment variables
load_dotenv()


class PromptLoader:
    """Load prompts from file system based on language and version"""

    def __init__(self):
        self.prompts_dir = os.path.join(os.path.dirname(__file__), "prompts")

    def get_prompt_version(self) -> str:
        """Get prompt version from environment variable"""
        return os.getenv("PROMPT_VERSION", "EN").upper()

    def load_prompt_files(self, version: str) -> Dict[str, str]:
        """Load prompt files for specified version"""
        prompt_dir = os.path.join(self.prompts_dir, version)

        if not os.path.exists(prompt_dir):
            raise ValueError(f"Prompt version '{version}' not found. Available versions: EN, ZH, EN_2_0, ZH_2_0")

        # Load system prompt
        system_prompt_path = os.path.join(prompt_dir, "system_prompt.txt")
        if not os.path.exists(system_prompt_path):
            raise FileNotFoundError(f"System prompt not found: {system_prompt_path}")

        with open(system_prompt_path, 'r', encoding='utf-8') as f:
            system_prompt = f.read().strip()

        # Load user prompt
        user_prompt_path = os.path.join(prompt_dir, "user_prompt.txt")
        if not os.path.exists(user_prompt_path):
            raise FileNotFoundError(f"User prompt not found: {user_prompt_path}")

        with open(user_prompt_path, 'r', encoding='utf-8') as f:
            user_prompt = f.read().strip()

        # Load schema if exists
        schema_path = os.path.join(prompt_dir, "analysis_schema.json")
        schema = None
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)

        return {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "schema": schema
        }

    def get_dynamic_model(self, schema: Optional[Dict[str, Any]] = None):
        """Create dynamic Pydantic model based on schema"""
        if not schema:
            # Use default model
            return PaperAnalysis

        # Create dynamic fields based on schema
        fields = {}
        for field_name, field_desc in schema.items():
            fields[field_name] = (str, Field(description=field_desc))

        # Create dynamic model
        DynamicPaperAnalysis = type('DynamicPaperAnalysis', (BaseModel,), fields)
        return DynamicPaperAnalysis


class PaperAnalysis(BaseModel):
    """Default structured output for paper analysis"""
    title: str = Field(description="Paper title")
    summary: str = Field(description="Brief summary of the paper's content")
    problem: str = Field(description="What problem the paper addresses")
    solution: str = Field(description="How the paper solves the problem")
    limitations: str = Field(description="Limitations or unresolved issues")
    key_contributions: str = Field(description="Main contributions of the paper")


class PaperAnalyzer:
    """Paper analyzer using LangChain and OpenAI"""

    def __init__(self, model_name="gpt-4o", temperature=0.1, prompt_version=None):
        """
        Initialize the paper analyzer

        Args:
            model_name (str): OpenAI model name
            temperature (float): Response randomness (0-1)
            prompt_version (str): Prompt version to use (EN, ZH, EN_2_0, ZH_2_0)
        """
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )

        # Initialize prompt loader
        self.prompt_loader = PromptLoader()

        # Get prompt version
        self.prompt_version = prompt_version or self.prompt_loader.get_prompt_version()

        # Load prompts
        self.prompts = self.prompt_loader.load_prompt_files(self.prompt_version)

        # Create output parser - use dict output instead of pydantic model for simplicity
        self.parser = JsonOutputParser()

        # Create prompt template - add format instructions to system prompt
        system_prompt_with_format = self.prompts["system_prompt"].format(
            format_instructions=self.parser.get_format_instructions()
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt_with_format),
            ("user", self.prompts["user_prompt"])
        ])

        # Create the chain
        self.chain = self.prompt | self.llm | self.parser

    def analyze_paper(self, paper_text: str, max_length: int = 8000) -> Dict[str, Any]:
        """
        Analyze a paper from markdown text

        Args:
            paper_text (str): Paper content in markdown format
            max_length (int): Maximum characters to analyze (to avoid token limits)

        Returns:
            Dict[str, Any]: Structured analysis results
        """
        # Truncate text if too long
        if len(paper_text) > max_length:
            paper_text = paper_text[:max_length] + "\n\n[Note: Paper truncated due to length limitations]"

        try:
            # Run the analysis
            result = self.chain.invoke({
                "paper_text": paper_text,
                "format_instructions": self.parser.get_format_instructions()
            })

            return result

        except Exception as e:
            print(f"Error analyzing paper: {e}")
            return {
                "error": str(e),
                "title": "Analysis Failed",
                "summary": "Unable to analyze the paper due to an error.",
                "problem": "N/A",
                "solution": "N/A",
                "limitations": "N/A",
                "key_contributions": "N/A"
            }

    def analyze_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a paper from a PDF or text file

        Args:
            file_path (str): Path to PDF or text file

        Returns:
            Dict[str, Any]: Structured analysis results
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return {
                    "error": f"File not found: {file_path}",
                    "title": "File Not Found",
                    "summary": "The specified file could not be found.",
                    "problem": "N/A",
                    "solution": "N/A",
                    "limitations": "N/A",
                    "key_contributions": "N/A"
                }

            # Determine file type and extract text
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == '.pdf':
                # Handle PDF file
                if pdf_to_markdown is None:
                    return {
                        "error": "PDF support not available. pdf_parser.py not found.",
                        "title": "PDF Support Error",
                        "summary": "PDF parsing is not available in this environment.",
                        "problem": "N/A",
                        "solution": "N/A",
                        "limitations": "N/A",
                        "key_contributions": "N/A"
                    }

                print(f"Processing PDF file: {file_path}")
                paper_text = pdf_to_markdown(file_path, extract_images=False)

            elif file_ext in ['.txt', '.md', '.markdown']:
                # Handle text file
                print(f"Processing text file: {file_path}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    paper_text = f.read()

            else:
                return {
                    "error": f"Unsupported file type: {file_ext}. Supported formats: PDF, TXT, MD, MARKDOWN",
                    "title": "Unsupported File Type",
                    "summary": f"The file type '{file_ext}' is not supported.",
                    "problem": "N/A",
                    "solution": "N/A",
                    "limitations": "N/A",
                    "key_contributions": "N/A"
                }

            return self.analyze_paper(paper_text)

        except Exception as e:
            print(f"Error processing file: {e}")
            return {
                "error": str(e),
                "title": "File Processing Error",
                "summary": f"Unable to process the file due to an error: {str(e)}",
                "problem": "N/A",
                "solution": "N/A",
                "limitations": "N/A",
                "key_contributions": "N/A"
            }

    def save_analysis(self, analysis: Dict[str, Any], output_path: str):
        """
        Save analysis results to a JSON file

        Args:
            analysis (Dict[str, Any]): Analysis results
            output_path (str): Output file path
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            print(f"Analysis saved to: {output_path}")
        except Exception as e:
            print(f"Error saving analysis: {e}")


def format_analysis_output(analysis: Dict[str, Any], prompt_version="EN") -> str:
    """
    Format analysis results for display

    Args:
        analysis (Dict[str, Any]): Analysis results
        prompt_version (str): Prompt version used for analysis

    Returns:
        str: Formatted output
    """
    print(analysis)
    if "error" in analysis:
        return f"Error: {analysis['error']}"

    # Dynamic formatting based on prompt version
    if prompt_version.startswith("ZH"):
        title_key = "论文标题" if "论文标题" in analysis else "title"
        summary_key = "论文内容的全面概述" if "论文内容的全面概述" in analysis else "summary"
        problem_key = "研究问题与挑战" if "研究问题与挑战" in analysis else "problem"
        solution_key = "方法论与技术路线" if "方法论与技术路线" in analysis else "solution"
        limitations_key = "技术局限与未解决问题" if "技术局限与未解决问题" in analysis else "limitations"
        contributions_key = "主要学术贡献" if "主要学术贡献" in analysis else "key_contributions"
        significance_key = "研究意义与影响" if "研究意义与影响" in analysis else "research_significance"

        output = f"""
{'='*60}
论文分析结果
{'='*60}

📋 标题: {analysis.get(title_key, 'N/A')}

📄 概述:
{analysis.get(summary_key, 'N/A')}

❓ 研究问题:
{analysis.get(problem_key, 'N/A')}

💡 解决方案:
{analysis.get(solution_key, 'N/A')}

⚠️  局限性:
{analysis.get(limitations_key, 'N/A')}

🎯 主要贡献:
{analysis.get(contributions_key, 'N/A')}

{'='*60}
"""
        if significance_key in analysis:
            output += f"""
🔬 研究意义:
{analysis.get(significance_key, 'N/A')}

{'='*60}
"""
    else:
        output = f"""
{'='*60}
PAPER ANALYSIS RESULTS
{'='*60}

📋 TITLE: {analysis.get('title', 'N/A')}

📄 SUMMARY:
{analysis.get('summary', 'N/A')}

❓ PROBLEM ADDRESSED:
{analysis.get('problem', 'N/A')}

💡 SOLUTION APPROACH:
{analysis.get('solution', 'N/A')}

⚠️  LIMITATIONS:
{analysis.get('limitations', 'N/A')}

🎯 KEY CONTRIBUTIONS:
{analysis.get('key_contributions', 'N/A')}

{'='*60}
"""
        if "research_significance" in analysis:
            output += f"""
🔬 RESEARCH SIGNIFICANCE:
{analysis.get('research_significance', 'N/A')}

{'='*60}
"""
    return output


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Analyze academic papers using AI')
    parser.add_argument('input_file', help='Path to PDF or text file containing paper content (supports: .pdf, .txt, .md, .markdown)')
    parser.add_argument('--output', '-o', help='Output file path (optional)')
    parser.add_argument('--model', default='gpt-4o', help='OpenAI model name (default: gpt-4o)')
    parser.add_argument('--temperature', type=float, default=0.1, help='Response temperature (0-1, default: 0.1)')
    parser.add_argument('--max-length', type=int, default=8000, help='Maximum characters to analyze (default: 8000)')
    parser.add_argument('--prompt-version', help='Prompt version to use (EN, ZH, EN_2_0, ZH_2_0). Default: EN or set via PROMPT_VERSION env var')

    args = parser.parse_args()

    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        exit(1)

    # Initialize analyzer
    analyzer = PaperAnalyzer(
        model_name=args.model,
        temperature=args.temperature,
        prompt_version=args.prompt_version
    )

    # Show prompt version being used
    print(f"Using prompt version: {analyzer.prompt_version}")

    # Analyze paper
    print(f"Analyzing paper: {args.input_file}")
    analysis = analyzer.analyze_from_file(args.input_file)

    # Display results
    print(format_analysis_output(analysis, analyzer.prompt_version))

    # Save results if output path specified
    if args.output:
        analyzer.save_analysis(analysis, args.output)
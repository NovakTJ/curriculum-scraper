import os
import glob
import re
import json
import time
import uuid
from tqdm import tqdm
import requests

'''
Not needed summarizing script, unused in the final pipeline
'''


class ClaudeSummarizer:
    def __init__(self, source_dir="ordered_text", output_dir="summarized_content", window_size=4, claude_api_key=None):
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.window_size = window_size
        self.claude_api_key = claude_api_key or os.environ.get("CLAUDE_API_KEY")
        self.batch_api_url = "https://api.anthropic.com/v1/messages/batches"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def extract_page_number(self, filename):
        match = re.match(r'page_(\d+)_extracted_text\.txt', os.path.basename(filename))
        if match:
            return int(match.group(1))
        return 0

    def read_text_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return ""

    def create_sliding_windows(self, files):
        files.sort(key=self.extract_page_number)
        windows = []
        for i in range(0, len(files), self.window_size):
            window = files[i:i+self.window_size]
            windows.append(window)
        return windows

    def create_batch_request(self, windows):
        """Create a batch request for multiple summarization tasks"""
        requests_data = []
        
        for i, window in enumerate(windows):
            window_content = "\n\n".join([self.read_text_file(f) for f in window])
            page_range = f"{self.extract_page_number(window[0])}-{self.extract_page_number(window[-1])}"
            
            prompt = f"""
            Extract specific concepts, guidelines, and C++ features from the following course material. Format as structured lists for exam generation context.

            {window_content[:8000]}  # Limit content to avoid token limits

            Output format:

            ## C++ FEATURES & SYNTAX:
            - [Specific feature with exact syntax/usage]
            - [Another specific feature]

            ## OBJECT-ORIENTED CONCEPTS:
            - [Specific OOP concept with details]
            - [Another OOP concept]

            ## PROGRAMMING GUIDELINES & PRINCIPLES:
            - [Specific guideline or best practice]
            - [Another guideline]

            ## KEY DEFINITIONS & TERMINOLOGY:
            - [Term]: [Precise definition]
            - [Another term]: [Definition]

            ## CODE EXAMPLES & PATTERNS:
            - [Specific coding pattern or example]
            - [Another pattern]

            Requirements:
            - Be SPECIFIC (e.g., "virtual function override syntax" not "virtual functions")
            - Include exact C++ keywords, operators, and syntax where mentioned
            - Extract concrete rules, not general statements
            - Focus on exam-testable content
            - No prose - only structured lists
            """
            
            request_data = {
                "custom_id": f"window_{page_range}",
                "params": {
                    "model": "claude-3-haiku-20240307",  # Using Haiku for cost efficiency
                    "max_tokens": 1000,
                    "temperature": 0.1,  # Lower temperature for more structured output
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
            }
            requests_data.append(request_data)
            
        return requests_data

    def submit_batch(self, requests_data):
        """Submit a batch request to Claude"""
        headers = {
            "x-api-key": self.claude_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        batch_data = {
            "requests": requests_data
        }
        
        response = requests.post(self.batch_api_url, headers=headers, json=batch_data)
        
        if response.status_code == 200:
            result = response.json()
            return result["id"]
        else:
            print(f"Batch submission error: {response.status_code} {response.text}")
            return None

    def check_batch_status(self, batch_id):
        """Check the status of a batch request"""
        headers = {
            "x-api-key": self.claude_api_key,
            "anthropic-version": "2023-06-01"
        }
        
        response = requests.get(f"{self.batch_api_url}/{batch_id}", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Batch status check error: {response.status_code} {response.text}")
            return None

    def get_batch_results(self, batch_id):
        """Get the results of a completed batch"""
        headers = {
            "x-api-key": self.claude_api_key,
            "anthropic-version": "2023-06-01"
        }
        
        response = requests.get(f"{self.batch_api_url}/{batch_id}/results", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Batch results error: {response.status_code} {response.text}")
            return None

    def wait_for_batch_completion(self, batch_id, max_wait_time=3600):
        """Wait for batch to complete, checking every 30 seconds"""
        start_time = time.time()
        
        print(f"Waiting for batch {batch_id} to complete...")
        
        while time.time() - start_time < max_wait_time:
            status_data = self.check_batch_status(batch_id)
            
            if status_data:
                status = status_data.get("processing_status")
                print(f"Batch status: {status}")
                
                if status == "ended":
                    return True
                elif status == "failed":
                    print("Batch processing failed!")
                    return False
            
            time.sleep(30)  # Wait 30 seconds before checking again
        
        print("Batch processing timed out!")
        return False

    def summarize_with_claude(self, content):
        """Fallback method for individual requests if batch fails"""
        prompt = f"""
        Extract specific concepts, guidelines, and C++ features from the following course material. Format as structured lists for exam generation context.

        {content}

        Output format:

        ## C++ FEATURES & SYNTAX:
        - [Specific feature with exact syntax/usage]
        - [Another specific feature]

        ## OBJECT-ORIENTED CONCEPTS:
        - [Specific OOP concept with details]
        - [Another OOP concept]

        ## PROGRAMMING GUIDELINES & PRINCIPLES:
        - [Specific guideline or best practice]
        - [Another guideline]

        ## KEY DEFINITIONS & TERMINOLOGY:
        - [Term]: [Precise definition]
        - [Another term]: [Definition]

        ## CODE EXAMPLES & PATTERNS:
        - [Specific coding pattern or example]
        - [Another pattern]

        Requirements:
        - Be SPECIFIC (e.g., "virtual function override syntax" not "virtual functions")
        - Include exact C++ keywords, operators, and syntax where mentioned
        - Extract concrete rules, not general statements
        - Focus on exam-testable content
        - No prose - only structured lists
        """
        headers = {
            "x-api-key": self.claude_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        data = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 1000,
            "temperature": 0.1,  # Lower temperature for structured output
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            return result["content"][0]["text"] if "content" in result and result["content"] else ""
        else:
            print(f"Claude API error: {response.status_code} {response.text}")
            return ""

    def process(self):
        """Process all files using batch API for cost efficiency"""
        files = glob.glob(os.path.join(self.source_dir, "page_*_extracted_text.txt"))
        windows = self.create_sliding_windows(files)
        
        print(f"Processing {len(windows)} windows using batch API...")
        
        # Create batch request
        batch_requests = self.create_batch_request(windows)
        
        # Submit batch
        batch_id = self.submit_batch(batch_requests)
        
        if not batch_id:
            print("Batch submission failed, falling back to individual requests...")
            return self.process_individual_requests(windows)
        
        print(f"Batch submitted with ID: {batch_id}")
        
        # Wait for completion
        if not self.wait_for_batch_completion(batch_id):
            print("Batch processing failed, falling back to individual requests...")
            return self.process_individual_requests(windows)
        
        # Get results
        batch_results = self.get_batch_results(batch_id)
        
        if not batch_results:
            print("Failed to get batch results, falling back to individual requests...")
            return self.process_individual_requests(windows)
        
        # Process results
        all_summaries = []
        results_by_id = {result["custom_id"]: result for result in batch_results}
        
        for window in windows:
            page_range = f"{self.extract_page_number(window[0])}-{self.extract_page_number(window[-1])}"
            custom_id = f"window_{page_range}"
            
            if custom_id in results_by_id:
                result = results_by_id[custom_id]
                if result["result"]["type"] == "succeeded":
                    summary = result["result"]["message"]["content"][0]["text"]
                else:
                    summary = f"Batch processing failed for this window: {result['result'].get('error', 'Unknown error')}"
            else:
                summary = "No result found in batch response"
            
            summary_data = {
                "page_range": page_range,
                "pages": [self.extract_page_number(f) for f in window],
                "summary": summary
            }
            all_summaries.append(summary_data)
            
            # Save each summary as markdown
            md_filename = f"pages_{page_range}_summary.md"
            with open(os.path.join(self.output_dir, md_filename), 'w', encoding='utf-8') as f:
                f.write(f"# Summary for Pages {page_range}\n\n{summary}\n")
        
        # Save all summaries as JSON
        with open(os.path.join(self.output_dir, "all_summaries.json"), 'w', encoding='utf-8') as f:
            json.dump(all_summaries, f, indent=2)
        
        print("Batch summarization complete!")
        return all_summaries

    def process_individual_requests(self, windows):
        """Fallback method using individual API requests"""
        print("Processing with individual requests...")
        all_summaries = []
        
        for window in tqdm(windows, desc="Summarizing windows"):
            window_content = "\n\n".join([self.read_text_file(f) for f in window])
            page_range = f"{self.extract_page_number(window[0])}-{self.extract_page_number(window[-1])}"
            summary = self.summarize_with_claude(window_content)
            
            summary_data = {
                "page_range": page_range,
                "pages": [self.extract_page_number(f) for f in window],
                "summary": summary
            }
            all_summaries.append(summary_data)
            
            # Save each summary as markdown
            md_filename = f"pages_{page_range}_summary.md"
            with open(os.path.join(self.output_dir, md_filename), 'w', encoding='utf-8') as f:
                f.write(f"# Summary for Pages {page_range}\n\n{summary}\n")
        
        # Save all summaries as JSON
        with open(os.path.join(self.output_dir, "all_summaries.json"), 'w', encoding='utf-8') as f:
            json.dump(all_summaries, f, indent=2)
        
        print("Individual request summarization complete!")
        return all_summaries

if __name__ == "__main__":
    claude_api_key = os.environ.get("CLAUDE_API_KEY")
    if not claude_api_key:
        print("Please set your CLAUDE_API_KEY environment variable")
        print("export CLAUDE_API_KEY='your-api-key-here'")
        exit(1)
    
    summarizer = ClaudeSummarizer(window_size=6, claude_api_key=claude_api_key)  # Increased window size for batch efficiency
    summarizer.process()

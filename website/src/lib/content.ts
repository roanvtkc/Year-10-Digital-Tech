import fs from 'node:fs';
import path from 'node:path';
import matter from 'gray-matter';
import { marked } from 'marked';

const CONTENT_BASE = path.join(process.cwd(), '..', 'content');

export interface ContentFile {
  slug: string;
  title: string;
  content: string;
  html: string;
  frontmatter: Record<string, unknown>;
  path: string;
}

export function readMarkdownFile(filePath: string): ContentFile | null {
  try {
    const fullPath = path.join(CONTENT_BASE, filePath);
    if (!fs.existsSync(fullPath)) {
      return null;
    }

    const fileContent = fs.readFileSync(fullPath, 'utf-8');
    const { data, content } = matter(fileContent);

    const titleMatch = content.match(/^#\s+(.+)$/m);
    const title = (data.title as string) || (titleMatch ? titleMatch[1] : path.basename(filePath, '.md'));
    const html = marked(content) as string;
    const slug = path.basename(filePath, '.md');

    return {
      slug,
      title,
      content,
      html,
      frontmatter: data,
      path: filePath,
    };
  } catch (error) {
    console.error(`Error reading file ${filePath}:`, error);
    return null;
  }
}

export function listMarkdownFiles(dirPath: string): string[] {
  try {
    const fullPath = path.join(CONTENT_BASE, dirPath);
    if (!fs.existsSync(fullPath)) {
      return [];
    }

    const files = fs.readdirSync(fullPath);
    return files
      .filter(f => f.endsWith('.md') && !f.startsWith('_'))
      .map(f => path.join(dirPath, f));
  } catch (error) {
    console.error(`Error listing directory ${dirPath}:`, error);
    return [];
  }
}

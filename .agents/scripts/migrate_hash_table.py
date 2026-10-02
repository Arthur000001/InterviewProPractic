import re
import os

practice_file = '/media/artur/BEA6-BBCE/InterviewPro/.notes/companies/ozon/topic_05_practice.html'
theory_file = '/media/artur/BEA6-BBCE/InterviewPro/.notes/companies/ozon/topic_02_go_theory.html'

with open(practice_file, 'r', encoding='utf-8') as f:
    practice_content = f.read()

# Extract the block
pattern = re.compile(r'(\s*<details class="key-question" id="ozon-main-topic_05_practice-2">.*?</details>)', re.DOTALL)
match = pattern.search(practice_content)

if not match:
    print("Could not find Task 2 in practice file")
    exit(1)

block = match.group(1)

# Remove the block from practice file
new_practice_content = practice_content.replace(block, '')
with open(practice_file, 'w', encoding='utf-8') as f:
    f.write(new_practice_content)

print("Removed Task 2 from topic_05_practice.html")

# Modify the block for theory file
new_block = block.replace('id="ozon-main-topic_05_practice-2"', 'id="ozon-main-topic_02_go_theory-28"')
new_block = new_block.replace('<strong>Задача 2.</strong>', '<strong>28.</strong>')

# Remove the Go Playground button
new_block = re.sub(r'<span class="question-actions">.*?</span>', '', new_block, flags=re.DOTALL)

# Clean up summary style if any
new_block = re.sub(r'style="display: flex; align-items: flex-start; justify-content: space-between; gap: 14px;"', '', new_block)

# Replace the code block
new_code = """package main

import (
	"fmt"
	"hash/fnv"
)

const loadFactorThreshold = 0.75

type Node struct {
	Key   string
	Value string
	Next  *Node
}

type HashTable struct {
	buckets []*Node
	size    int
	count   int
}

func NewHashTable(size int) *HashTable {
	return &HashTable{
		buckets: make([]*Node, size),
		size:    size,
		count:   0,
	}
}

func (h *HashTable) hash(key string, size int) int {
	hasher := fnv.New32a()
	hasher.Write([]byte(key))
	return int(hasher.Sum32()) % size
}

func (h *HashTable) Set(key, value string) {
	if float64(h.count+1)/float64(h.size) > loadFactorThreshold {
		h.rehash()
	}

	idx := h.hash(key, h.size)
	head := h.buckets[idx]
	for curr := head; curr != nil; curr = curr.Next {
		if curr.Key == key {
			curr.Value = value
			return
		}
	}
	h.buckets[idx] = &Node{Key: key, Value: value, Next: head}
	h.count++
}

func (h *HashTable) Get(key string) (string, bool) {
	idx := h.hash(key, h.size)
	for curr := h.buckets[idx]; curr != nil; curr = curr.Next {
		if curr.Key == key {
			return curr.Value, true
		}
	}
	return "", false
}

func (h *HashTable) rehash() {
	newSize := h.size * 2
	newBuckets := make([]*Node, newSize)

	for _, head := range h.buckets {
		for curr := head; curr != nil; curr = curr.Next {
			idx := h.hash(curr.Key, newSize)
			newNode := &Node{Key: curr.Key, Value: curr.Value, Next: newBuckets[idx]}
			newBuckets[idx] = newNode
		}
	}
	
	h.buckets = newBuckets
	h.size = newSize
}

func main() {
	ht := NewHashTable(4)
	ht.Set("city", "Moscow")
	ht.Set("cluster", "prod-cluster-01")
	ht.Set("region", "RU")
	ht.Set("az", "ru-central1-a") // Триггер рехеша (4/4 > 0.75)

	if val, ok := ht.Get("city"); ok {
		fmt.Printf("Found: city = %s\\n", val)
	}
	fmt.Printf("Current buckets size: %d, items count: %d\\n", ht.size, ht.count)
}"""

new_block = re.sub(r'<pre><code class="language-go">.*?</code></pre>', f'<pre><code class="language-go">{new_code}</code></pre>', new_block, flags=re.DOTALL)

# Read theory file and append
with open(theory_file, 'r', encoding='utf-8') as f:
    theory_content = f.read()

# Insert before </div>\n    </main>
insertion_point = theory_content.rfind('      </div>\n    </main>')
if insertion_point == -1:
    print("Could not find insertion point in theory file")
    exit(1)

new_theory_content = theory_content[:insertion_point] + new_block + '\n' + theory_content[insertion_point:]

with open(theory_file, 'w', encoding='utf-8') as f:
    f.write(new_theory_content)

print("Added Task 2 to topic_02_go_theory.html")
